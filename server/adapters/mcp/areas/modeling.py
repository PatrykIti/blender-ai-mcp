import asyncio
import re
from collections.abc import Callable
from typing import Any, Dict, List, Optional, Union

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_warning
from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.guided_contract import canonicalize_modeling_create_primitive_arguments
from server.adapters.mcp.guided_naming_policy import evaluate_guided_object_name
from server.adapters.mcp.router_helper import (
    route_tool_call,
    route_tool_call_async,
    route_tool_call_report,
    wrap_sync_tool_for_async_guided_finalizers,
)
from server.adapters.mcp.session_capabilities import (
    get_session_capability_state,
    get_session_capability_state_async,
    mark_guided_spatial_state_stale_async,
    register_guided_part_role,
    register_guided_part_role_async,
    set_session_capability_state_async,
)
from server.adapters.mcp.utils import parse_coordinate, parse_dict
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.adapters.mcp.vision.integration import maybe_attach_macro_vision
from server.adapters.mcp.vision.policy import choose_capture_preset_profile
from server.infrastructure.di import get_macro_handler, get_modeling_handler, get_vision_backend_resolver

MODELING_PUBLIC_TOOL_NAMES = (
    "macro_cutout_recess",
    "macro_finish_form",
    "modeling_create_primitive",
    "modeling_transform_object",
    "modeling_add_modifier",
    "modeling_apply_modifier",
    "modeling_convert_to_mesh",
    "modeling_join_objects",
    "modeling_separate_object",
    "modeling_list_modifiers",
    "modeling_set_origin",
    "metaball_create",
    "metaball_add_element",
    "metaball_to_mesh",
    "skin_create_skeleton",
    "skin_set_radius",
)

_CREATED_OBJECT_RESULT_PATTERN = re.compile(r"Created .+ named '(.+)'$")
_TRANSFORMED_OBJECT_RESULT_PATTERN = re.compile(r"Transformed object '(.+)'$")


def _extract_created_object_name(result: str) -> str | None:
    """Return the created object name from the canonical modeling success string."""

    for line in reversed(result.splitlines()):
        match = _CREATED_OBJECT_RESULT_PATTERN.search(line.strip())
        if match is None:
            continue
        object_name = match.group(1).strip()
        if object_name:
            return object_name
    return None


def _extract_transformed_object_name(result: str) -> str | None:
    """Return the transformed object name from the canonical modeling success string."""

    for line in reversed(result.splitlines()):
        match = _TRANSFORMED_OBJECT_RESULT_PATTERN.search(line.strip())
        if match is None:
            continue
        object_name = match.group(1).strip()
        if object_name:
            return object_name
    return None


def _extract_created_object_name_from_report_steps(report: Any) -> str | None:
    """Return the created object name from successful routed create steps."""

    if getattr(report, "error", None) is not None:
        return None

    for step in reversed(tuple(getattr(report, "steps", ()) or ())):
        if getattr(step, "tool_name", None) != "modeling_create_primitive":
            continue
        if getattr(step, "error", None) is not None:
            continue
        result = getattr(step, "result", None)
        if not isinstance(result, str):
            continue
        object_name = _extract_created_object_name(result)
        if object_name:
            return object_name
    return None


def _extract_transformed_object_name_from_report_steps(report: Any) -> str | None:
    """Return the transformed object name from successful routed transform steps."""

    if getattr(report, "error", None) is not None:
        return None

    for step in reversed(tuple(getattr(report, "steps", ()) or ())):
        if getattr(step, "tool_name", None) != "modeling_transform_object":
            continue
        if getattr(step, "error", None) is not None:
            continue
        result = getattr(step, "result", None)
        if not isinstance(result, str):
            continue
        object_name = _extract_transformed_object_name(result)
        if object_name:
            return object_name
    return None


def _has_transform_success(result: str, *, object_name: str) -> bool:
    return _extract_transformed_object_name(result) == object_name


def _emit_guided_naming_warning_from_report(ctx: Context, report: Any) -> None:
    """Surface router naming feedback when an async tool consumes a raw route report."""

    policy_context = getattr(report, "policy_context", None)
    if not isinstance(policy_context, dict):
        return
    naming_payload = policy_context.get("guided_naming")
    if not isinstance(naming_payload, dict):
        return
    if naming_payload.get("status") != "warning":
        return
    message = naming_payload.get("message")
    if message:
        ctx_warning(ctx, str(message))


def _maybe_register_guided_role(
    ctx: Context,
    *,
    object_name: str | None,
    guided_role: str | None,
    role_group: str | None,
) -> None:
    """Register one guided role only when an active guided flow exists."""

    if not guided_role:
        return

    session = get_session_capability_state(ctx)
    if session.guided_flow_state is None:
        return

    normalized_object_name = str(object_name or "").strip()
    if not normalized_object_name:
        return

    register_guided_part_role(
        ctx,
        object_name=normalized_object_name,
        role=guided_role,
        role_group=role_group,
    )


def _guided_create_requires_explicit_name(
    ctx: Context,
    *,
    guided_role: str | None,
    object_name: str | None,
) -> str | None:
    """Return one actionable error when guided create would rely on an auto-generated name."""

    if not guided_role:
        return None

    session = get_session_capability_state(ctx)
    if session.guided_flow_state is None:
        return None

    normalized_object_name = str(object_name or "").strip()
    if normalized_object_name:
        return None

    domain_profile = str((session.guided_flow_state or {}).get("domain_profile") or "").strip()
    current_step = str((session.guided_flow_state or {}).get("current_step") or "").strip() or None
    suggested_names: list[str] = []
    if domain_profile in {"generic", "creature", "building"}:
        try:
            decision = evaluate_guided_object_name(
                object_name="Object",
                role=guided_role,
                domain_profile=domain_profile,  # type: ignore[arg-type]
                current_step=current_step,
            )
            suggested_names = list(decision.suggested_names or [])
        except Exception:
            suggested_names = []

    suggestion_suffix = f" Suggested names: {', '.join(suggested_names)}." if suggested_names else ""
    return (
        "Guided execution requires an explicit semantic `name` when `guided_role=...` is used on "
        "modeling_create_primitive(...). Auto-generated Blender names are not accepted for semantic role "
        f"registration.{suggestion_suffix}"
    )


def _register_tool(target: Any, fn: Any, tool_name: str) -> Any:
    """Register one modeling tool on a FastMCP-compatible target."""

    public_tool = globals().get(tool_name)
    public_fn = getattr(public_tool, "fn", public_tool)
    public_docstring = getattr(public_fn, "__doc__", None)
    if public_docstring and public_fn is not fn:
        fn.__doc__ = public_docstring
    fn = wrap_sync_tool_for_async_guided_finalizers(fn, tool_name=tool_name)
    return target.tool(fn, name=tool_name, tags=set(get_capability_tags("modeling")))


def _legacy_route_report_result(report: Any) -> Any:
    if report.error is None and len(report.steps) == 1:
        result = report.steps[0].result
        if not isinstance(result, str):
            return result
    return report.to_legacy_text()


async def _hydrate_sync_route_session(ctx: Context) -> None:
    """Mirror async FastMCP session state into request state for sync router-policy helpers."""

    state = await get_session_capability_state_async(ctx)
    await set_session_capability_state_async(ctx, state)


async def _maybe_register_guided_role_async(
    ctx: Context,
    *,
    object_name: str | None,
    guided_role: str | None,
    role_group: str | None,
) -> None:
    """Register one guided role only when an active guided flow exists."""

    if not guided_role:
        return

    session = await get_session_capability_state_async(ctx)
    if session.guided_flow_state is None:
        return

    normalized_object_name = str(object_name or "").strip()
    if not normalized_object_name:
        return

    await register_guided_part_role_async(
        ctx,
        object_name=normalized_object_name,
        role=guided_role,
        role_group=role_group,
    )


def _route_tool_call_report_for_context(
    ctx: Context,
    *,
    tool_name: str,
    params: Dict[str, Any],
    direct_executor: Callable[[], Any],
) -> Any:
    """Run sync router policy with the explicit async FastMCP context in scope."""

    token = None
    current_context = None
    try:
        from fastmcp.server.context import _current_context  # type: ignore

        current_context = _current_context
        token = current_context.set(ctx)
    except Exception:
        current_context = None
        token = None
    try:
        return route_tool_call_report(tool_name=tool_name, params=params, direct_executor=direct_executor)
    finally:
        if current_context is not None and token is not None:
            current_context.reset(token)


def register_modeling_tools(target: Any) -> Dict[str, Any]:
    """Register public modeling tools on a FastMCP server or LocalProvider."""

    impls = {
        "macro_cutout_recess": _macro_cutout_recess_impl,
        "macro_finish_form": _macro_finish_form_impl,
        "modeling_create_primitive": _modeling_create_primitive_impl_async,
        "modeling_transform_object": _modeling_transform_object_impl_async,
        "modeling_add_modifier": _modeling_add_modifier_impl,
        "modeling_apply_modifier": _modeling_apply_modifier_impl,
        "modeling_convert_to_mesh": _modeling_convert_to_mesh_impl,
        "modeling_join_objects": _modeling_join_objects_impl,
        "modeling_separate_object": _modeling_separate_object_impl,
        "modeling_list_modifiers": _modeling_list_modifiers_impl,
        "modeling_set_origin": _modeling_set_origin_impl,
        "metaball_create": _metaball_create_impl,
        "metaball_add_element": _metaball_add_element_impl,
        "metaball_to_mesh": _metaball_to_mesh_impl,
        "skin_create_skeleton": _skin_create_skeleton_impl,
        "skin_set_radius": _skin_set_radius_impl,
    }
    return {tool_name: _register_tool(target, impls[tool_name], tool_name) for tool_name in MODELING_PUBLIC_TOOL_NAMES}


async def _resolve_macro_capture_profile(ctx: Context) -> str | None:
    resolver = get_vision_backend_resolver()
    if not resolver.runtime_config.enabled:
        return None
    session = await get_session_capability_state_async(ctx)
    return choose_capture_preset_profile(
        reference_image_count=len(session.reference_images or []),
        max_images=resolver.runtime_config.max_images,
    )


async def _macro_cutout_recess_impl(
    ctx: Context,
    target_object: str,
    width: float,
    height: float,
    depth: float,
    face: str = "front",
    offset: Union[str, List[float], None] = None,
    mode: str = "recess",
    bevel_width: Optional[float] = None,
    bevel_segments: int = 2,
    cleanup: str = "delete",
    cutter_name: Optional[str] = None,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for cutter-based recess/cutout creation on one target object.

    Use this when the intent is "make a recess/cutout here" rather than manually chaining
    primitive creation, transform, bevel, boolean, and cleanup steps yourself.

    Current first slice:
    - axis-aligned box cutter only
    - face placement via target world-space bounding box (`front`/`back`/`left`/`right`/`top`/`bottom`)
    - `recess` or `cut_through` mode
    - optional bevel on the cutter
    - cleanup by delete/hide/keep

    Args:
        target_object: Existing object that will receive the cutout.
        width: In-plane width of the cutter footprint on the chosen face.
        height: Secondary in-plane size of the cutter footprint on the chosen face.
        depth: Recess depth (for `recess`) or minimum sizing hint (for `cut_through`).
        face: Which bbox face to target (`front`, `back`, `left`, `right`, `top`, `bottom`).
        offset: Optional world-axis offset `[x, y, z]` applied after face-center placement.
        mode: `recess` or `cut_through`.
        bevel_width: Optional bevel width for the cutter.
        bevel_segments: Segments for the optional bevel.
        cleanup: What to do with the cutter after boolean (`delete`, `hide`, `keep`).
        cutter_name: Optional explicit helper object name.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            parsed_offset = parse_coordinate(offset) or [0.0, 0.0, 0.0]
            payload = get_macro_handler().cutout_recess(
                target_object=target_object,
                width=width,
                height=height,
                depth=depth,
                face=face,
                offset=parsed_offset,
                mode=mode,
                bevel_width=bevel_width,
                bevel_segments=bevel_segments,
                cleanup=cleanup,
                cutter_name=cutter_name,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_cutout_recess",
                intent=f"{mode} cutout on '{target_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_cutout_recess",
        params={
            "target_object": target_object,
            "width": width,
            "height": height,
            "depth": depth,
            "face": face,
            "offset": offset,
            "mode": mode,
            "bevel_width": bevel_width,
            "bevel_segments": bevel_segments,
            "cleanup": cleanup,
            "cutter_name": cutter_name,
        },
        direct_executor=execute,
    )
    if isinstance(result, MacroExecutionReportContract):
        return result if result.status == "failed" else await maybe_attach_macro_vision(ctx, result)
    if isinstance(result, dict):
        if result.get("status") == "failed" or result.get("error"):
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_cutout_recess",
                intent=f"{mode} cutout on '{target_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(result.get("error") or result),
            )
        contract = MacroExecutionReportContract.model_validate(result)
        return contract if contract.status == "failed" else await maybe_attach_macro_vision(ctx, contract)
    return MacroExecutionReportContract(
        status="failed",
        macro_name="macro_cutout_recess",
        intent=f"{mode} cutout on '{target_object}'",
        actions_taken=[],
        requires_followup=False,
        error=str(result),
    )


async def _macro_finish_form_impl(
    ctx: Context,
    target_object: str,
    preset: str = "rounded_housing",
    bevel_width: Optional[float] = None,
    bevel_segments: Optional[int] = None,
    subsurf_levels: Optional[int] = None,
    thickness: Optional[float] = None,
    solidify_offset: float = 0.0,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for common hard-surface finishing presets.

    Use this when the intent is "finish this form" rather than manually deciding and ordering
    bevel, subdivision, or solidify modifiers yourself.

    Presets:
    - `rounded_housing`: bevel + subdivision for softened enclosure forms
    - `panel_finish`: light bevel-only finish for crisp panels
    - `shell_thicken`: solidify-only shell thickening
    - `smooth_subdivision`: subdivision-only smoothing preset

    Args:
        target_object: Existing object that will receive the finishing stack.
        preset: Bounded finishing preset to apply.
        bevel_width: Optional override for presets that use bevel.
        bevel_segments: Optional override for presets that use bevel.
        subsurf_levels: Optional override for presets that use subdivision.
        thickness: Optional override for the `shell_thicken` preset.
        solidify_offset: Optional solidify offset for the `shell_thicken` preset.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            payload = get_macro_handler().finish_form(
                target_object=target_object,
                preset=preset,
                bevel_width=bevel_width,
                bevel_segments=bevel_segments,
                subsurf_levels=subsurf_levels,
                thickness=thickness,
                solidify_offset=solidify_offset,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_finish_form",
                intent=f"apply '{preset}' finishing preset to '{target_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_finish_form",
        params={
            "target_object": target_object,
            "preset": preset,
            "bevel_width": bevel_width,
            "bevel_segments": bevel_segments,
            "subsurf_levels": subsurf_levels,
            "thickness": thickness,
            "solidify_offset": solidify_offset,
        },
        direct_executor=execute,
    )
    if isinstance(result, MacroExecutionReportContract):
        return result if result.status == "failed" else await maybe_attach_macro_vision(ctx, result)
    if isinstance(result, dict):
        if result.get("status") == "failed" or result.get("error"):
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_finish_form",
                intent=f"apply '{preset}' finishing preset to '{target_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(result.get("error") or result),
            )
        contract = MacroExecutionReportContract.model_validate(result)
        return contract if contract.status == "failed" else await maybe_attach_macro_vision(ctx, contract)
    return MacroExecutionReportContract(
        status="failed",
        macro_name="macro_finish_form",
        intent=f"apply '{preset}' finishing preset to '{target_object}'",
        actions_taken=[],
        requires_followup=False,
        error=str(result),
    )


def _modeling_create_primitive_impl(
    ctx: Context,
    primitive_type: str,
    radius: float = 1.0,
    size: float = 2.0,
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    rotation: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: str = None,
    scale: Union[str, List[float], None] = None,
    segments: int | None = None,
    rings: int | None = None,
    subdivisions: int | None = None,
    collection_name: str | None = None,
    guided_role: str | None = None,
    role_group: str | None = None,
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Creates a 3D primitive object.

    Workflow: START → new object | AFTER → modeling_transform, scene_set_mode('EDIT')

    Public guided usage: create the primitive with its base shape first, then
    call `modeling_transform_object(scale=...)` for non-uniform scale.

    Args:
        primitive_type: "Cube", "Sphere", "Cylinder", "Plane", "Cone", "Monkey", "Torus".
        radius: Radius for Sphere/Cylinder/Cone.
        size: Size for Cube/Plane/Monkey.
        location: [x, y, z] coordinates. Can be a list [0.0, 0.0, 0.0] or string '[0.0, 0.0, 0.0]'.
        rotation: [rx, ry, rz] rotation in radians. Can be a list or string.
        name: Optional name for the new object.
        scale: Compatibility-only drift catcher. The guided public surface
            requires a follow-up `modeling_transform_object(scale=...)` call.
        segments: Compatibility-only drift catcher for rejected primitive-only topology knobs.
        rings: Compatibility-only drift catcher for rejected primitive-only topology knobs.
        subdivisions: Compatibility-only drift catcher for rejected primitive-only topology knobs.
        collection_name: Compatibility-only drift catcher. Move/link after
            creation with `collection_manage(...)`.
    """
    canonical_arguments = canonicalize_modeling_create_primitive_arguments(
        {
            key: value
            for key, value in {
                "primitive_type": primitive_type,
                "radius": radius,
                "size": size,
                "location": location,
                "rotation": rotation,
                "name": name,
                "scale": scale,
                "segments": segments,
                "rings": rings,
                "subdivisions": subdivisions,
                "collection_name": collection_name,
                "guided_role": guided_role,
                "role_group": role_group,
            }.items()
            if value is not None
        }
    )
    primitive_type_value = str(canonical_arguments["primitive_type"])
    radius_value = float(canonical_arguments.get("radius", radius))
    size_value = float(canonical_arguments.get("size", size))
    location_value = canonical_arguments.get("location", location)
    rotation_value = canonical_arguments.get("rotation", rotation)
    name_value = canonical_arguments.get("name")
    guided_name_error = _guided_create_requires_explicit_name(
        ctx,
        guided_role=guided_role,
        object_name=str(name_value).strip() if name_value else None,
    )
    if guided_name_error is not None:
        raise ValueError(guided_name_error)

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location_value) or [0.0, 0.0, 0.0]
            parsed_rotation = parse_coordinate(rotation_value) or [0.0, 0.0, 0.0]
            return handler.create_primitive(
                primitive_type_value,
                radius_value,
                size_value,
                parsed_location,
                parsed_rotation,
                name_value,
            )
        except (RuntimeError, ValueError) as e:
            return str(e)

    result = route_tool_call(
        tool_name="modeling_create_primitive",
        params={
            "primitive_type": primitive_type_value,
            "radius": radius_value,
            "size": size_value,
            "location": location_value,
            "rotation": rotation_value,
            "name": name_value,
            "guided_role": guided_role,
            "role_group": role_group,
        },
        direct_executor=execute,
    )
    created_object_name = _extract_created_object_name(result) if isinstance(result, str) else None
    if guided_role and created_object_name is not None:
        _maybe_register_guided_role(
            ctx,
            object_name=created_object_name,
            guided_role=guided_role,
            role_group=role_group,
        )
    return result


async def _modeling_create_primitive_impl_async(
    ctx: Context,
    primitive_type: str,
    radius: float = 1.0,
    size: float = 2.0,
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    rotation: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: str = None,
    scale: Union[str, List[float], None] = None,
    segments: int | None = None,
    rings: int | None = None,
    subdivisions: int | None = None,
    collection_name: str | None = None,
    guided_role: str | None = None,
    role_group: str | None = None,
) -> str:
    """Async registered variant that awaits guided session updates."""

    await _hydrate_sync_route_session(ctx)
    canonical_arguments = canonicalize_modeling_create_primitive_arguments(
        {
            key: value
            for key, value in {
                "primitive_type": primitive_type,
                "radius": radius,
                "size": size,
                "location": location,
                "rotation": rotation,
                "name": name,
                "scale": scale,
                "segments": segments,
                "rings": rings,
                "subdivisions": subdivisions,
                "collection_name": collection_name,
                "guided_role": guided_role,
                "role_group": role_group,
            }.items()
            if value is not None
        }
    )
    primitive_type_value = str(canonical_arguments["primitive_type"])
    radius_value = float(canonical_arguments.get("radius", radius))
    size_value = float(canonical_arguments.get("size", size))
    location_value = canonical_arguments.get("location", location)
    rotation_value = canonical_arguments.get("rotation", rotation)
    name_value = canonical_arguments.get("name")
    guided_name_error = _guided_create_requires_explicit_name(
        ctx,
        guided_role=guided_role,
        object_name=str(name_value).strip() if name_value else None,
    )
    if guided_name_error is not None:
        raise ValueError(guided_name_error)

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location_value) or [0.0, 0.0, 0.0]
            parsed_rotation = parse_coordinate(rotation_value) or [0.0, 0.0, 0.0]
            return handler.create_primitive(
                primitive_type_value,
                radius_value,
                size_value,
                parsed_location,
                parsed_rotation,
                name_value,
            )
        except (RuntimeError, ValueError) as e:
            return str(e)

    report = await asyncio.to_thread(
        _route_tool_call_report_for_context,
        ctx,
        tool_name="modeling_create_primitive",
        params={
            "primitive_type": primitive_type_value,
            "radius": radius_value,
            "size": size_value,
            "location": location_value,
            "rotation": rotation_value,
            "name": name_value,
            "guided_role": guided_role,
            "role_group": role_group,
        },
        direct_executor=execute,
    )
    _emit_guided_naming_warning_from_report(ctx, report)
    result = _legacy_route_report_result(report)
    created_object_name = _extract_created_object_name_from_report_steps(report)
    if created_object_name is not None:
        await mark_guided_spatial_state_stale_async(
            ctx,
            tool_name="modeling_create_primitive",
            family="primary_masses" if guided_role in {"body_core", "head_mass", "tail_mass"} else None,
            reason="modeling_create_primitive",
        )
    if created_object_name is not None:
        await _maybe_register_guided_role_async(
            ctx,
            object_name=created_object_name,
            guided_role=guided_role,
            role_group=role_group,
        )
    return str(result)


def modeling_create_primitive(
    ctx: Context,
    primitive_type: str,
    radius: float = 1.0,
    size: float = 2.0,
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    rotation: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: str = None,
    scale: Union[str, List[float], None] = None,
    segments: int | None = None,
    rings: int | None = None,
    subdivisions: int | None = None,
    collection_name: str | None = None,
    guided_role: str | None = None,
    role_group: str | None = None,
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Creates a 3D primitive object.

    Workflow: START → new object | AFTER → modeling_transform, scene_set_mode('EDIT')

    Public guided usage: create the primitive with its base shape first, then
    call `modeling_transform_object(scale=...)` for non-uniform scale.

    Args:
        primitive_type: "Cube", "Sphere", "Cylinder", "Plane", "Cone", "Monkey", "Torus".
        radius: Radius for Sphere/Cylinder/Cone.
        size: Size for Cube/Plane/Monkey.
        location: [x, y, z] coordinates. Can be a list [0.0, 0.0, 0.0] or string '[0.0, 0.0, 0.0]'.
        rotation: [rx, ry, rz] rotation in radians. Can be a list or string.
        name: Optional name for the new object.
    """
    return _modeling_create_primitive_impl(
        ctx,
        primitive_type,
        radius,
        size,
        location,
        rotation,
        name,
        scale,
        segments,
        rings,
        subdivisions,
        collection_name,
        guided_role,
        role_group,
    )


def _modeling_transform_object_impl(
    ctx: Context,
    name: str,
    location: Union[str, List[float], None] = None,
    rotation: Union[str, List[float], None] = None,
    scale: Union[str, List[float], None] = None,
    guided_role: str | None = None,
    role_group: str | None = None,
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Transforms (move, rotate, scale) an existing object.

    Workflow: AFTER → modeling_create_primitive | BEFORE → scene_set_mode('EDIT')

    Args:
        name: Name of the object.
        location: New [x, y, z] coordinates (optional). Can be a list [0.0, 0.0, 2.0] or string '[0.0, 0.0, 2.0]'.
        rotation: New [rx, ry, rz] rotation in radians (optional). Can be a list or string.
        scale: New [sx, sy, sz] scale factors (optional). Can be a list or string.
    """

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            parsed_rotation = parse_coordinate(rotation)
            parsed_scale = parse_coordinate(scale)
            return handler.transform_object(name, parsed_location, parsed_rotation, parsed_scale)
        except (RuntimeError, ValueError) as e:
            return str(e)

    result = route_tool_call(
        tool_name="modeling_transform_object",
        params={
            "name": name,
            "location": location,
            "rotation": rotation,
            "scale": scale,
            "guided_role": guided_role,
            "role_group": role_group,
        },
        direct_executor=execute,
    )
    transformed_object_name = _extract_transformed_object_name(result) if isinstance(result, str) else None
    if guided_role and transformed_object_name is not None:
        _maybe_register_guided_role(
            ctx,
            object_name=transformed_object_name,
            guided_role=guided_role,
            role_group=role_group,
        )
    return result


async def _modeling_transform_object_impl_async(
    ctx: Context,
    name: str,
    location: Union[str, List[float], None] = None,
    rotation: Union[str, List[float], None] = None,
    scale: Union[str, List[float], None] = None,
    guided_role: str | None = None,
    role_group: str | None = None,
) -> str:
    """Async registered variant that awaits guided session updates."""

    await _hydrate_sync_route_session(ctx)

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            parsed_rotation = parse_coordinate(rotation)
            parsed_scale = parse_coordinate(scale)
            return handler.transform_object(name, parsed_location, parsed_rotation, parsed_scale)
        except (RuntimeError, ValueError) as e:
            return str(e)

    report = await asyncio.to_thread(
        _route_tool_call_report_for_context,
        ctx,
        tool_name="modeling_transform_object",
        params={
            "name": name,
            "location": location,
            "rotation": rotation,
            "scale": scale,
            "guided_role": guided_role,
            "role_group": role_group,
        },
        direct_executor=execute,
    )
    _emit_guided_naming_warning_from_report(ctx, report)
    result = _legacy_route_report_result(report)
    transformed_object_name = _extract_transformed_object_name_from_report_steps(report)
    if transformed_object_name is not None:
        await mark_guided_spatial_state_stale_async(
            ctx,
            tool_name="modeling_transform_object",
            reason="modeling_transform_object",
        )
    if transformed_object_name is not None:
        await _maybe_register_guided_role_async(
            ctx,
            object_name=transformed_object_name,
            guided_role=guided_role,
            role_group=role_group,
        )
    return str(result)


def modeling_transform_object(
    ctx: Context,
    name: str,
    location: Union[str, List[float], None] = None,
    rotation: Union[str, List[float], None] = None,
    scale: Union[str, List[float], None] = None,
    guided_role: str | None = None,
    role_group: str | None = None,
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Transforms (move, rotate, scale) an existing object.

    Workflow: AFTER → modeling_create_primitive | BEFORE → scene_set_mode('EDIT')

    Args:
        name: Name of the object.
        location: New [x, y, z] coordinates (optional). Can be a list [0.0, 0.0, 2.0] or string '[0.0, 0.0, 2.0]'.
        rotation: New [rx, ry, rz] rotation in radians (optional). Can be a list or string.
        scale: New [sx, sy, sz] scale factors (optional). Can be a list or string.
    """
    return _modeling_transform_object_impl(ctx, name, location, rotation, scale, guided_role, role_group)


def _modeling_add_modifier_impl(
    ctx: Context, name: str, modifier_type: str, properties: Union[str, Dict[str, Any], None] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Adds a modifier to an object.
    Use this object-level modifier tool when you want a controlled non-destructive stack change.

    Workflow: NON-DESTRUCTIVE | AFTER → modeling_apply_modifier

    Args:
        name: Object name.
        modifier_type: Type of modifier (e.g., 'SUBSURF', 'BEVEL', 'MIRROR', 'BOOLEAN').
        properties: Dictionary of modifier properties to set (e.g., {'levels': 2}). Can be a dict or string '{"levels": 2}'.
            BOOLEAN note: to set the cutter/target object, pass `{"object": "<ObjectName>"}` (or alias `object_name`)
            where the value is the name of an existing Blender object.
    """

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_properties = parse_dict(properties)
            return handler.add_modifier(name, modifier_type, parsed_properties)
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="modeling_add_modifier",
        params={"name": name, "modifier_type": modifier_type, "properties": properties},
        direct_executor=execute,
    )


def modeling_add_modifier(
    ctx: Context, name: str, modifier_type: str, properties: Union[str, Dict[str, Any], None] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Adds a modifier to an object.
    Use this object-level modifier tool when you want a controlled non-destructive stack change.

    Workflow: NON-DESTRUCTIVE | AFTER → modeling_apply_modifier

    Args:
        name: Object name.
        modifier_type: Type of modifier (e.g., 'SUBSURF', 'BEVEL', 'MIRROR', 'BOOLEAN').
        properties: Dictionary of modifier properties to set (e.g., {'levels': 2}). Can be a dict or string '{"levels": 2}'.
            BOOLEAN note: to set the cutter/target object, pass `{"object": "<ObjectName>"}` (or alias `object_name`)
            where the value is the name of an existing Blender object.
    """
    return _modeling_add_modifier_impl(ctx, name, modifier_type, properties)


def _modeling_apply_modifier_impl(ctx: Context, name: str, modifier_name: str) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Applies a modifier, making its changes permanent to the mesh.

    Workflow: BEFORE → modeling_list_modifiers | DESTRUCTIVE - bakes changes

    Args:
        name: Object name.
        modifier_name: The name of the modifier to apply.
    """
    return route_tool_call(
        tool_name="modeling_apply_modifier",
        params={"name": name, "modifier_name": modifier_name},
        direct_executor=lambda: get_modeling_handler().apply_modifier(name, modifier_name),
    )


def modeling_apply_modifier(ctx: Context, name: str, modifier_name: str) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Applies a modifier, making its changes permanent to the mesh.

    Workflow: BEFORE → modeling_list_modifiers | DESTRUCTIVE - bakes changes

    Args:
        name: Object name.
        modifier_name: The name of the modifier to apply.
    """
    return _modeling_apply_modifier_impl(ctx, name, modifier_name)


def _modeling_convert_to_mesh_impl(ctx: Context, name: str) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts a non-mesh object (Curve, Text, Surface) to a mesh.

    Workflow: USE FOR → Curve/Text → Mesh | AFTER → scene_set_mode('EDIT')

    Args:
        name: The name of the object to convert.
    """
    return route_tool_call(
        tool_name="modeling_convert_to_mesh",
        params={"name": name},
        direct_executor=lambda: get_modeling_handler().convert_to_mesh(name),
    )


def modeling_convert_to_mesh(ctx: Context, name: str) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts a non-mesh object (Curve, Text, Surface) to a mesh.

    Workflow: USE FOR → Curve/Text → Mesh | AFTER → scene_set_mode('EDIT')

    Args:
        name: The name of the object to convert.
    """
    return _modeling_convert_to_mesh_impl(ctx, name)


def _modeling_join_objects_impl(ctx: Context, object_names: List[str]) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Joins multiple mesh objects into a single mesh.
    IMPORTANT: The LAST object in the list becomes the Active Object (Base).

    Workflow: BEFORE → mesh_boolean workflow | AFTER → mesh_select_linked

    Args:
        object_names: A list of names of the objects to join.
    """
    return route_tool_call(
        tool_name="modeling_join_objects",
        params={"object_names": object_names},
        direct_executor=lambda: get_modeling_handler().join_objects(object_names),
    )


def modeling_join_objects(ctx: Context, object_names: List[str]) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Joins multiple mesh objects into a single mesh.
    IMPORTANT: The LAST object in the list becomes the Active Object (Base).

    Workflow: BEFORE → mesh_boolean workflow | AFTER → mesh_select_linked

    Args:
        object_names: A list of names of the objects to join.
    """
    return _modeling_join_objects_impl(ctx, object_names)


def _modeling_separate_object_impl(ctx: Context, name: str, type: str = "LOOSE") -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Separates a mesh into new objects (LOOSE, SELECTED, MATERIAL).

    Workflow: AFTER → mesh_select_linked | USE → split mesh islands

    Args:
        name: The name of the object to separate.
        type: The separation method: "LOOSE", "SELECTED", or "MATERIAL".
    """

    def execute():
        handler = get_modeling_handler()
        try:
            result = handler.separate_object(name, type)
            return str(result)
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="modeling_separate_object", params={"name": name, "type": type}, direct_executor=execute
    )


def modeling_separate_object(ctx: Context, name: str, type: str = "LOOSE") -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Separates a mesh into new objects (LOOSE, SELECTED, MATERIAL).

    Workflow: AFTER → mesh_select_linked | USE → split mesh islands

    Args:
        name: The name of the object to separate.
        type: The separation method: "LOOSE", "SELECTED", or "MATERIAL".
    """
    return _modeling_separate_object_impl(ctx, name, type)


def _modeling_list_modifiers_impl(ctx: Context, name: str) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Lists all modifiers currently on the specified object.

    Workflow: READ-ONLY | BEFORE → modeling_apply_modifier

    Args:
        name: The name of the object.
    """

    def execute():
        handler = get_modeling_handler()
        try:
            modifiers = handler.get_modifiers(name)
            return str(modifiers)
        except RuntimeError as e:
            return str(e)

    return route_tool_call(tool_name="modeling_list_modifiers", params={"name": name}, direct_executor=execute)


def modeling_list_modifiers(ctx: Context, name: str) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Lists all modifiers currently on the specified object.

    Workflow: READ-ONLY | BEFORE → modeling_apply_modifier

    Args:
        name: The name of the object.
    """
    return _modeling_list_modifiers_impl(ctx, name)


# Internal function - exposed through grouped scene inspection
def _modeling_get_modifier_data(
    ctx: Context, object_name: str, modifier_name: Optional[str] = None, include_node_tree: bool = False
) -> Dict[str, Any]:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns full modifier properties.
    """
    handler = get_modeling_handler()
    try:
        return handler.get_modifier_data(object_name, modifier_name, include_node_tree)
    except RuntimeError as e:
        return {"error": str(e)}


def _modeling_set_origin_impl(ctx: Context, name: str, type: str) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Sets the origin point of an object.

    Workflow: AFTER → geometry changes | BEFORE → modeling_transform

    Args:
        name: Object name.
        type: Origin type (e.g., 'ORIGIN_GEOMETRY', 'ORIGIN_CURSOR', 'ORIGIN_CENTER_OF_MASS').
    """
    return route_tool_call(
        tool_name="modeling_set_origin",
        params={"name": name, "type": type},
        direct_executor=lambda: get_modeling_handler().set_origin(name, type),
    )


def modeling_set_origin(ctx: Context, name: str, type: str) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Sets the origin point of an object.

    Workflow: AFTER → geometry changes | BEFORE → modeling_transform

    Args:
        name: Object name.
        type: Origin type (e.g., 'ORIGIN_GEOMETRY', 'ORIGIN_CURSOR', 'ORIGIN_CENTER_OF_MASS').
    """
    return _modeling_set_origin_impl(ctx, name, type)


# ==============================================================================
# TASK-038-1: Metaball Tools
# ==============================================================================


def _metaball_create_impl(
    ctx: Context,
    name: str = "Metaball",
    location: Union[str, List[float], None] = None,
    element_type: str = "BALL",
    radius: float = 1.0,
    resolution: float = 0.2,
    threshold: float = 0.6,
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a metaball object.

    Metaballs automatically merge when close together, creating organic blob shapes.
    Perfect for: veins, tumors, fat deposits, cellular structures, organs.

    Element types:
        - BALL: Spherical element (default)
        - CAPSULE: Tubular element for blood vessels
        - PLANE: Flat disc element
        - ELLIPSOID: Stretched sphere
        - CUBE: Cubic element

    Workflow: AFTER → metaball_add_element | metaball_to_mesh

    Args:
        name: Name for the metaball object
        location: World position [x, y, z]
        element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
        radius: Initial element radius (default 1.0)
        resolution: Surface resolution - lower = higher quality (default 0.2)
        threshold: Merge threshold for elements (default 0.6)

    Examples:
        metaball_create(name="Heart", element_type="ELLIPSOID", radius=1.5)
        metaball_create(name="Tumor", resolution=0.1) -> Higher quality
    """

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            return handler.metaball_create(
                name=name,
                location=parsed_location,
                element_type=element_type,
                radius=radius,
                resolution=resolution,
                threshold=threshold,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="metaball_create",
        params={
            "name": name,
            "location": location,
            "element_type": element_type,
            "radius": radius,
            "resolution": resolution,
            "threshold": threshold,
        },
        direct_executor=execute,
    )


def metaball_create(
    ctx: Context,
    name: str = "Metaball",
    location: Union[str, List[float], None] = None,
    element_type: str = "BALL",
    radius: float = 1.0,
    resolution: float = 0.2,
    threshold: float = 0.6,
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a metaball object.

    Metaballs automatically merge when close together, creating organic blob shapes.
    Perfect for: veins, tumors, fat deposits, cellular structures, organs.

    Element types:
        - BALL: Spherical element (default)
        - CAPSULE: Tubular element for blood vessels
        - PLANE: Flat disc element
        - ELLIPSOID: Stretched sphere
        - CUBE: Cubic element

    Workflow: AFTER → metaball_add_element | metaball_to_mesh

    Args:
        name: Name for the metaball object
        location: World position [x, y, z]
        element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
        radius: Initial element radius (default 1.0)
        resolution: Surface resolution - lower = higher quality (default 0.2)
        threshold: Merge threshold for elements (default 0.6)

    Examples:
        metaball_create(name="Heart", element_type="ELLIPSOID", radius=1.5)
        metaball_create(name="Tumor", resolution=0.1) -> Higher quality
    """
    return _metaball_create_impl(
        ctx,
        name,
        location,
        element_type,
        radius,
        resolution,
        threshold,
    )


def _metaball_add_element_impl(
    ctx: Context,
    metaball_name: str,
    element_type: str = "BALL",
    location: Union[str, List[float], None] = None,
    radius: float = 1.0,
    stiffness: float = 2.0,
) -> str:
    """
    [OBJECT MODE] Adds element to existing metaball.

    Multiple elements merge together based on proximity and stiffness.
    Use CAPSULE for tubular structures (blood vessels, nerves).

    Workflow: BEFORE → metaball_create | AFTER → metaball_to_mesh

    Args:
        metaball_name: Name of target metaball object
        element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
        location: Position relative to metaball origin [x, y, z]
        radius: Element radius (default 1.0)
        stiffness: How strongly it merges with other elements (default 2.0)

    Examples:
        metaball_add_element("Heart", location=[0.5, 0, 0.3], radius=0.8)
        metaball_add_element("Vessel", element_type="CAPSULE", radius=0.2)
    """

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            return handler.metaball_add_element(
                metaball_name=metaball_name,
                element_type=element_type,
                location=parsed_location,
                radius=radius,
                stiffness=stiffness,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="metaball_add_element",
        params={
            "metaball_name": metaball_name,
            "element_type": element_type,
            "location": location,
            "radius": radius,
            "stiffness": stiffness,
        },
        direct_executor=execute,
    )


def metaball_add_element(
    ctx: Context,
    metaball_name: str,
    element_type: str = "BALL",
    location: Union[str, List[float], None] = None,
    radius: float = 1.0,
    stiffness: float = 2.0,
) -> str:
    """
    [OBJECT MODE] Adds element to existing metaball.

    Multiple elements merge together based on proximity and stiffness.
    Use CAPSULE for tubular structures (blood vessels, nerves).

    Workflow: BEFORE → metaball_create | AFTER → metaball_to_mesh

    Args:
        metaball_name: Name of target metaball object
        element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
        location: Position relative to metaball origin [x, y, z]
        radius: Element radius (default 1.0)
        stiffness: How strongly it merges with other elements (default 2.0)

    Examples:
        metaball_add_element("Heart", location=[0.5, 0, 0.3], radius=0.8)
        metaball_add_element("Vessel", element_type="CAPSULE", radius=0.2)
    """
    return _metaball_add_element_impl(
        ctx,
        metaball_name,
        element_type,
        location,
        radius,
        stiffness,
    )


def _metaball_to_mesh_impl(
    ctx: Context,
    metaball_name: str,
    apply_resolution: bool = True,
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts metaball to mesh.

    Required for:
    - Mesh editing operations (extrude, bevel, etc.)
    - Export to game engines
    - Further sculpting with dyntopo

    Workflow: AFTER → sculpt_enable_dyntopo | mesh_remesh_voxel (cleanup)

    Args:
        metaball_name: Name of metaball to convert
        apply_resolution: Whether to apply current resolution (default True)

    Examples:
        metaball_to_mesh("Heart") -> Converts to mesh for editing
    """
    return route_tool_call(
        tool_name="metaball_to_mesh",
        params={"metaball_name": metaball_name, "apply_resolution": apply_resolution},
        direct_executor=lambda: get_modeling_handler().metaball_to_mesh(
            metaball_name=metaball_name, apply_resolution=apply_resolution
        ),
    )


def metaball_to_mesh(
    ctx: Context,
    metaball_name: str,
    apply_resolution: bool = True,
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts metaball to mesh.

    Required for:
    - Mesh editing operations (extrude, bevel, etc.)
    - Export to game engines
    - Further sculpting with dyntopo

    Workflow: AFTER → sculpt_enable_dyntopo | mesh_remesh_voxel (cleanup)

    Args:
        metaball_name: Name of metaball to convert
        apply_resolution: Whether to apply current resolution (default True)

    Examples:
        metaball_to_mesh("Heart") -> Converts to mesh for editing
    """
    return _metaball_to_mesh_impl(ctx, metaball_name, apply_resolution)


# ==============================================================================
# TASK-038-6: Skin Modifier Workflow
# ==============================================================================


def _skin_create_skeleton_impl(
    ctx: Context,
    name: str = "Skeleton",
    vertices: Union[str, List[List[float]], None] = None,
    edges: Union[str, List[List[int]], None] = None,
    location: Union[str, List[float], None] = None,
) -> str:
    """
    [OBJECT MODE][SCENE] Creates skeleton mesh for Skin modifier.

    Define vertices as path points, edges connect them.
    Skin modifier will create tubular mesh around this skeleton.

    Use case: blood vessels, nerves, tree branches, tentacles.

    Workflow: AFTER → modeling_add_modifier(type="SKIN") | skin_set_radius

    Args:
        name: Name for skeleton object (default "Skeleton")
        vertices: List of vertex positions [[x,y,z], ...] (default [[0,0,0], [0,0,1]])
        edges: List of edge connections [[v1, v2], ...] (auto-connect sequentially if None)
        location: World position [x, y, z]

    Examples:
        skin_create_skeleton(name="Artery", vertices=[[0,0,0], [0,0,1], [0.3,0,1.5]])
        skin_create_skeleton(name="Branch", vertices=[[0,0,0], [0,0,1], [0.5,0,1.5], [-0.5,0,1.5]], edges=[[0,1], [1,2], [1,3]])
    """

    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            parsed_vertices = parse_coordinate(vertices) if isinstance(vertices, str) else vertices
            parsed_edges = parse_coordinate(edges) if isinstance(edges, str) else edges
            return handler.skin_create_skeleton(
                name=name,
                vertices=parsed_vertices,
                edges=parsed_edges,
                location=parsed_location,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="skin_create_skeleton",
        params={"name": name, "vertices": vertices, "edges": edges, "location": location},
        direct_executor=execute,
    )


def skin_create_skeleton(
    ctx: Context,
    name: str = "Skeleton",
    vertices: Union[str, List[List[float]], None] = None,
    edges: Union[str, List[List[int]], None] = None,
    location: Union[str, List[float], None] = None,
) -> str:
    """
    [OBJECT MODE][SCENE] Creates skeleton mesh for Skin modifier.

    Define vertices as path points, edges connect them.
    Skin modifier will create tubular mesh around this skeleton.

    Use case: blood vessels, nerves, tree branches, tentacles.

    Workflow: AFTER → modeling_add_modifier(type="SKIN") | skin_set_radius

    Args:
        name: Name for skeleton object (default "Skeleton")
        vertices: List of vertex positions [[x,y,z], ...] (default [[0,0,0], [0,0,1]])
        edges: List of edge connections [[v1, v2], ...] (auto-connect sequentially if None)
        location: World position [x, y, z]

    Examples:
        skin_create_skeleton(name="Artery", vertices=[[0,0,0], [0,0,1], [0.3,0,1.5]])
        skin_create_skeleton(name="Branch", vertices=[[0,0,0], [0,0,1], [0.5,0,1.5], [-0.5,0,1.5]], edges=[[0,1], [1,2], [1,3]])
    """
    return _skin_create_skeleton_impl(ctx, name, vertices, edges, location)


def _skin_set_radius_impl(
    ctx: Context,
    object_name: str,
    vertex_index: Optional[int] = None,
    radius_x: float = 0.25,
    radius_y: float = 0.25,
) -> str:
    """
    [EDIT MODE] Sets skin radius at vertices.

    Each vertex can have different X/Y radius for elliptical cross-sections.

    Use case: Varying vessel thickness (aorta thicker than capillaries).

    Workflow: BEFORE → skin_create_skeleton | AFTER → modeling_apply_modifier

    Args:
        object_name: Name of object with skin modifier
        vertex_index: Specific vertex index (None = all selected/all vertices)
        radius_x: X radius for elliptical cross-section (default 0.25)
        radius_y: Y radius for elliptical cross-section (default 0.25)

    Examples:
        skin_set_radius("Artery", vertex_index=0, radius_x=0.15) -> Thick at base
        skin_set_radius("Artery", radius_x=0.05, radius_y=0.05) -> Thin everywhere
    """
    return route_tool_call(
        tool_name="skin_set_radius",
        params={"object_name": object_name, "vertex_index": vertex_index, "radius_x": radius_x, "radius_y": radius_y},
        direct_executor=lambda: get_modeling_handler().skin_set_radius(
            object_name=object_name, vertex_index=vertex_index, radius_x=radius_x, radius_y=radius_y
        ),
    )


def skin_set_radius(
    ctx: Context,
    object_name: str,
    vertex_index: Optional[int] = None,
    radius_x: float = 0.25,
    radius_y: float = 0.25,
) -> str:
    """
    [EDIT MODE] Sets skin radius at vertices.

    Each vertex can have different X/Y radius for elliptical cross-sections.

    Use case: Varying vessel thickness (aorta thicker than capillaries).

    Workflow: BEFORE → skin_create_skeleton | AFTER → modeling_apply_modifier

    Args:
        object_name: Name of object with skin modifier
        vertex_index: Specific vertex index (None = all selected/all vertices)
        radius_x: X radius for elliptical cross-section (default 0.25)
        radius_y: Y radius for elliptical cross-section (default 0.25)

    Examples:
        skin_set_radius("Artery", vertex_index=0, radius_x=0.15) -> Thick at base
        skin_set_radius("Artery", radius_x=0.05, radius_y=0.05) -> Thin everywhere
    """
    return _skin_set_radius_impl(ctx, object_name, vertex_index, radius_x, radius_y)
