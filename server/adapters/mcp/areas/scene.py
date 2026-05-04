import asyncio
from typing import Any, Dict, List, Literal, Optional, Union

from fastmcp import Context
from fastmcp.utilities.types import Image
from pydantic import ValidationError

from server.adapters.mcp.areas.scene_create_configure import (
    execute_scene_configure,
    execute_scene_configure_color_management,
    execute_scene_configure_render_settings,
    execute_scene_configure_world,
    execute_scene_create,
    execute_scene_create_camera,
    execute_scene_create_empty,
    execute_scene_create_light,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    guided_scope_mismatch_message as _guided_scope_mismatch_message,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    guided_scope_requirement_error as _guided_scope_requirement_error,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    hydrate_sync_route_session as _hydrate_sync_route_session,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    legacy_route_report_result as _legacy_route_report_result,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    report_has_successful_scene_clean_step as _report_has_successful_scene_clean_step,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    route_tool_call_report_for_context as _route_tool_call_report_for_context,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    should_require_explicit_guided_scope as _should_require_explicit_guided_scope,
)
from server.adapters.mcp.areas.scene_guided_runtime import (
    view_diagnostics_can_complete_guided_check as _view_diagnostics_can_complete_guided_check,
)
from server.adapters.mcp.areas.scene_inspect import (
    execute_scene_inspect,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_color_management as _scene_inspect_color_management_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_constraints as _scene_get_constraints_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_material_slots as _scene_inspect_material_slots_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_mesh_topology as _scene_inspect_mesh_topology_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_modifier_data as _scene_inspect_modifier_data_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_modifiers as _scene_inspect_modifiers_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_object as _scene_inspect_object_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_render_settings as _scene_inspect_render_settings_impl,
)
from server.adapters.mcp.areas.scene_inspect import (
    inspect_scene_world as _scene_inspect_world_impl,
)
from server.adapters.mcp.areas.scene_measure_assert import (
    route_scene_assert_contact,
    route_scene_assert_containment,
    route_scene_assert_dimensions,
    route_scene_assert_proportion,
    route_scene_assert_symmetry,
    route_scene_measure_alignment,
    route_scene_measure_dimensions,
    route_scene_measure_distance,
    route_scene_measure_gap,
    route_scene_measure_overlap,
)
from server.adapters.mcp.areas.scene_object_utils import (
    route_scene_camera_focus,
    route_scene_camera_orbit,
    route_scene_clean_scene,
    route_scene_clean_scene_async,
    route_scene_delete_object,
    route_scene_duplicate_object,
    route_scene_get_custom_properties,
    route_scene_hide_object,
    route_scene_isolate_object,
    route_scene_list_objects,
    route_scene_rename_object,
    route_scene_set_active_object,
    route_scene_set_custom_property,
    route_scene_set_mode,
    route_scene_show_all_objects,
)
from server.adapters.mcp.areas.scene_spatial_graph import (
    route_scene_relation_graph,
    route_scene_relation_graph_async,
    route_scene_scope_graph,
    route_scene_scope_graph_async,
)
from server.adapters.mcp.areas.scene_state_reads import (
    execute_scene_compare_snapshot,
    execute_scene_context,
    execute_scene_get_bounding_box,
    execute_scene_get_hierarchy,
    execute_scene_get_origin_info,
    execute_scene_snapshot_state,
)
from server.adapters.mcp.areas.scene_state_reads import (
    get_scene_mode as _scene_get_mode_impl,
)
from server.adapters.mcp.areas.scene_state_reads import (
    list_scene_selection as _scene_list_selection_impl,
)
from server.adapters.mcp.areas.scene_view_diagnostics import (
    route_scene_view_diagnostics,
    route_scene_view_diagnostics_async,
)
from server.adapters.mcp.areas.scene_viewport import (
    format_viewport_output as _format_viewport_output_impl,
)
from server.adapters.mcp.areas.scene_viewport import (
    route_scene_get_viewport as _route_scene_get_viewport,
)
from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.contracts.scene import (
    SceneAssertContactContract,
    SceneAssertContainmentContract,
    SceneAssertDimensionsContract,
    SceneAssertProportionContract,
    SceneAssertSymmetryContract,
    SceneBoundingBoxContract,
    SceneConfigureResponseContract,
    SceneContextResponseContract,
    SceneCreateResponseContract,
    SceneCustomPropertiesContract,
    SceneHierarchyContract,
    SceneInspectResponseContract,
    SceneMeasureAlignmentContract,
    SceneMeasureDimensionsContract,
    SceneMeasureDistanceContract,
    SceneMeasureGapContract,
    SceneMeasureOverlapContract,
    SceneOriginInfoContract,
    SceneRelationGraphResponseContract,
    SceneScopeGraphResponseContract,
    SceneSnapshotDiffContract,
    SceneSnapshotStateContract,
    SceneViewDiagnosticsResponseContract,
)
from server.adapters.mcp.router_helper import (
    route_tool_call,
    route_tool_call_async,
    wrap_sync_tool_for_async_guided_finalizers,
)
from server.adapters.mcp.sampling.assistant_runner import run_inspection_summary_assistant
from server.adapters.mcp.sampling.result_types import to_inspection_assistant_contract
from server.adapters.mcp.session_capabilities import (
    describe_guided_flow_feedback,
    get_session_capability_state_async,
    mark_guided_spatial_state_stale_async,
    record_guided_flow_spatial_check_completion,
    record_guided_flow_spatial_check_completion_async,
    update_quality_gate_plan_from_relation_graph,
    update_quality_gate_plan_from_relation_graph_async,
)
from server.adapters.mcp.tasks.candidacy import get_tool_task_config
from server.adapters.mcp.tasks.task_bridge import (
    is_background_task_context,
    run_rpc_background_job,
)
from server.adapters.mcp.utils import parse_coordinate
from server.adapters.mcp.version_policy import get_versioned_tool_versions
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.adapters.mcp.vision.integration import maybe_attach_macro_vision
from server.adapters.mcp.vision.policy import choose_capture_preset_profile
from server.application.services.snapshot_diff import get_snapshot_diff_service
from server.infrastructure.di import get_macro_handler, get_scene_handler, get_vision_backend_resolver

SCENE_PUBLIC_TOOL_NAMES = (
    "scene_list_objects",
    "scene_delete_object",
    "scene_clean_scene",
    "scene_duplicate_object",
    "scene_set_active_object",
    "scene_context",
    "scene_inspect",
    "scene_configure",
    "scene_get_viewport",
    "scene_snapshot_state",
    "scene_compare_snapshot",
    "scene_create",
    "macro_relative_layout",
    "macro_attach_part_to_surface",
    "macro_align_part_with_contact",
    "macro_place_symmetry_pair",
    "macro_place_supported_pair",
    "macro_cleanup_part_intersections",
    "macro_adjust_relative_proportion",
    "macro_adjust_segment_chain_arc",
    "scene_set_mode",
    "scene_rename_object",
    "scene_hide_object",
    "scene_show_all_objects",
    "scene_isolate_object",
    "scene_camera_orbit",
    "scene_camera_focus",
    "scene_get_custom_properties",
    "scene_set_custom_property",
    "scene_get_hierarchy",
    "scene_get_bounding_box",
    "scene_get_origin_info",
    "scene_scope_graph",
    "scene_relation_graph",
    "scene_view_diagnostics",
    "scene_measure_distance",
    "scene_measure_dimensions",
    "scene_measure_gap",
    "scene_measure_alignment",
    "scene_measure_overlap",
    "scene_assert_contact",
    "scene_assert_dimensions",
    "scene_assert_containment",
    "scene_assert_symmetry",
    "scene_assert_proportion",
)


MacroErrorStatus = Literal["blocked", "failed"]


def _coerce_macro_error_status(value: object) -> MacroErrorStatus:
    """Narrow adapter-side fallback statuses to the contract's error states."""

    return "blocked" if value == "blocked" else "failed"


async def _finalize_macro_execution_result(
    ctx: Context,
    result: object,
    *,
    macro_name: str,
    intent: str,
) -> MacroExecutionReportContract:
    """Preserve structured macro reports before falling back to adapter errors."""

    if isinstance(result, MacroExecutionReportContract):
        contract = result
    elif isinstance(result, dict):
        try:
            contract = MacroExecutionReportContract.model_validate(result)
        except ValidationError:
            contract = MacroExecutionReportContract(
                status=_coerce_macro_error_status(result.get("status")),
                macro_name=macro_name,
                intent=intent,
                actions_taken=list(result.get("actions_taken") or []),
                requires_followup=bool(result.get("requires_followup")),
                error=str(result.get("error") or result),
            )
    else:
        contract = MacroExecutionReportContract(
            status="failed",
            macro_name=macro_name,
            intent=intent,
            actions_taken=[],
            requires_followup=False,
            error=str(result),
        )

    if contract.status in {"blocked", "failed"}:
        return contract
    return await maybe_attach_macro_vision(ctx, contract)


def _register_existing_tool(target: Any, tool_name: str) -> Any:
    """Register an existing scene tool on a FastMCP-compatible target."""

    async_tool = globals().get(f"_{tool_name}_async")
    public_tool = globals()[tool_name]
    tool = async_tool or public_tool
    fn = getattr(tool, "fn", tool)
    if async_tool is not None:
        public_fn = getattr(public_tool, "fn", public_tool)
        public_docstring = getattr(public_fn, "__doc__", None)
        if public_docstring:
            fn.__doc__ = public_docstring
    fn = wrap_sync_tool_for_async_guided_finalizers(fn, tool_name=tool_name)
    task_config = get_tool_task_config(tool_name)
    versions = get_versioned_tool_versions(tool_name)
    if versions:
        registered = None
        for version in versions:
            version_kwargs: Dict[str, Any] = {
                "name": tool_name,
                "version": version,
                "tags": set(get_capability_tags("scene")),
            }
            if task_config is not None:
                version_kwargs["task"] = task_config
            registered = target.tool(fn, **version_kwargs)
        return registered
    base_kwargs: Dict[str, Any] = {"name": tool_name, "tags": set(get_capability_tags("scene"))}
    if task_config is not None:
        base_kwargs["task"] = task_config
    return target.tool(fn, **base_kwargs)


def register_scene_tools(target: Any) -> Dict[str, Any]:
    """Register public scene tools on a FastMCP server or LocalProvider."""

    return {tool_name: _register_existing_tool(target, tool_name) for tool_name in SCENE_PUBLIC_TOOL_NAMES}


async def _resolve_macro_capture_profile(ctx: Context) -> str | None:
    resolver = get_vision_backend_resolver()
    if not resolver.runtime_config.enabled:
        return None
    session = await get_session_capability_state_async(ctx)
    return choose_capture_preset_profile(
        reference_image_count=len(session.reference_images or []),
        max_images=resolver.runtime_config.max_images,
    )


async def macro_relative_layout(
    ctx: Context,
    moving_object: str,
    reference_object: str,
    x_mode: Literal["none", "center", "min", "max"] = "center",
    y_mode: Literal["none", "center", "min", "max"] = "center",
    z_mode: Literal["none", "center", "min", "max"] = "none",
    contact_axis: Literal["X", "Y", "Z"] | None = None,
    contact_side: Literal["positive", "negative"] = "positive",
    gap: float = 0.0,
    offset: Union[str, List[float], None] = None,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for relative bbox-based layout between two objects.

    Use this when the intent is "place this part relative to that part" rather than manually
    inspecting bounding boxes, calculating coordinates, and moving the object yourself.

    Current first slice:
    - axis-aligned bbox layout only
    - per-axis alignment modes (`none`, `center`, `min`, `max`)
    - optional outside-face contact placement on one axis
    - optional post-layout world offset
    - deterministic verification hints via measure/assert tools

    Args:
        moving_object: Existing object that will be moved.
        reference_object: Existing object that stays fixed and provides the layout reference.
        x_mode: Alignment rule for the X axis.
        y_mode: Alignment rule for the Y axis.
        z_mode: Alignment rule for the Z axis when not using `contact_axis`.
        contact_axis: Optional axis for outside-face contact/gap placement (`X`, `Y`, `Z`).
        contact_side: Which side of the reference bbox to place the moving object on.
        gap: Optional non-negative spacing along the contact axis.
        offset: Optional world-axis offset `[x, y, z]` applied after the bounded layout placement.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            parsed_offset = parse_coordinate(offset) or [0.0, 0.0, 0.0]
            payload = get_macro_handler().relative_layout(
                moving_object=moving_object,
                reference_object=reference_object,
                x_mode=x_mode,
                y_mode=y_mode,
                z_mode=z_mode,
                contact_axis=contact_axis,
                contact_side=contact_side,
                gap=gap,
                offset=parsed_offset,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_relative_layout",
                intent=f"layout '{moving_object}' relative to '{reference_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_relative_layout",
        params={
            "moving_object": moving_object,
            "reference_object": reference_object,
            "x_mode": x_mode,
            "y_mode": y_mode,
            "z_mode": z_mode,
            "contact_axis": contact_axis,
            "contact_side": contact_side,
            "gap": gap,
            "offset": offset,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_relative_layout",
        intent=f"layout '{moving_object}' relative to '{reference_object}'",
    )


async def macro_attach_part_to_surface(
    ctx: Context,
    part_object: str,
    surface_object: str,
    surface_axis: Literal["X", "Y", "Z"],
    surface_side: Literal["positive", "negative"] = "positive",
    align_mode: Literal["none", "center", "min", "max"] = "center",
    gap: float = 0.0,
    max_mesh_nudge: float = 0.15,
    offset: Union[str, List[float], None] = None,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for seating one part onto another object's surface/body.

    Use this when the intent is "attach this part onto that surface" rather than
    manually composing a more generic relative layout call. The first slice keeps
    the attachment bounded:

    - one required surface axis (`X`, `Y`, `Z`)
    - one required surface side (`positive`, `negative`)
    - one shared tangential alignment mode for the two remaining axes; use
      `none` to preserve existing tangential offsets
    - optional non-negative contact gap
    - optional bounded mesh-surface nudge after bbox seating
    - optional world offset after seating

    Args:
        part_object: Existing object that will be seated onto the target surface/body.
        surface_object: Existing object that stays fixed and provides the target surface.
        surface_axis: Axis normal of the target surface (`X`, `Y`, `Z`).
        surface_side: Which side of the target surface bbox to attach against.
        align_mode: Alignment rule applied to the two axes tangent to the surface.
            Use `none` to preserve current tangential offsets.
        gap: Optional non-negative spacing along the surface normal.
        max_mesh_nudge: Maximum mesh-surface nearest-point nudge after bbox seating.
        offset: Optional world-axis offset `[x, y, z]` applied after seating.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            parsed_offset = parse_coordinate(offset) or [0.0, 0.0, 0.0]
            payload = get_macro_handler().attach_part_to_surface(
                part_object=part_object,
                surface_object=surface_object,
                surface_axis=surface_axis,
                surface_side=surface_side,
                align_mode=align_mode,
                gap=gap,
                max_mesh_nudge=max_mesh_nudge,
                offset=parsed_offset,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_attach_part_to_surface",
                intent=f"attach '{part_object}' to '{surface_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_attach_part_to_surface",
        params={
            "part_object": part_object,
            "surface_object": surface_object,
            "surface_axis": surface_axis,
            "surface_side": surface_side,
            "align_mode": align_mode,
            "gap": gap,
            "max_mesh_nudge": max_mesh_nudge,
            "offset": offset,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_attach_part_to_surface",
        intent=f"attach '{part_object}' to '{surface_object}'",
    )


async def macro_align_part_with_contact(
    ctx: Context,
    part_object: str,
    reference_object: str,
    target_relation: Literal["contact", "gap"] = "contact",
    gap: float = 0.0,
    align_mode: Literal["none", "center", "min", "max"] = "none",
    normal_axis: Literal["X", "Y", "Z"] | None = None,
    preserve_side: bool = True,
    max_nudge: float = 0.5,
    offset: Union[str, List[float], None] = None,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded repair macro for an already-related part pair.

    Use this when a part is already roughly attached, but truth tools still show
    a small gap, contact failure, or tangential drift that should be corrected
    with a minimal nudge instead of a fresh placement.

    Current first slice:
    - one part/reference pair only
    - truth-driven repair planning using gap/alignment/overlap/contact checks
    - inferred normal axis when possible
    - preserve current side by default when that side is clear
    - bounded `max_nudge` safety gate to avoid turning repair into re-placement

    Args:
        part_object: Existing object to repair.
        reference_object: Existing object that defines the desired relation.
        target_relation: Desired repaired relation: `contact` or explicit `gap`.
        gap: Target non-negative gap when `target_relation="gap"`. Must stay `0` for `contact`.
        align_mode: Optional tangential alignment rule for the two non-normal axes.
        normal_axis: Optional explicit normal axis. If omitted, the macro infers one when possible.
        preserve_side: If True, preserve the current side relation when it is clear.
        max_nudge: Maximum allowed total movement for the bounded repair.
        offset: Optional world-axis offset `[x, y, z]` applied after the repair target is computed.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            parsed_offset = parse_coordinate(offset) or [0.0, 0.0, 0.0]
            payload = get_macro_handler().align_part_with_contact(
                part_object=part_object,
                reference_object=reference_object,
                target_relation=target_relation,
                gap=gap,
                align_mode=align_mode,
                normal_axis=normal_axis,
                preserve_side=preserve_side,
                max_nudge=max_nudge,
                offset=parsed_offset,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_align_part_with_contact",
                intent=f"repair '{part_object}' relative to '{reference_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_align_part_with_contact",
        params={
            "part_object": part_object,
            "reference_object": reference_object,
            "target_relation": target_relation,
            "gap": gap,
            "align_mode": align_mode,
            "normal_axis": normal_axis,
            "preserve_side": preserve_side,
            "max_nudge": max_nudge,
            "offset": offset,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_align_part_with_contact",
        intent=f"repair '{part_object}' relative to '{reference_object}'",
    )


async def macro_place_symmetry_pair(
    ctx: Context,
    left_object: str,
    right_object: str,
    axis: Literal["X", "Y", "Z"] = "X",
    mirror_coordinate: float = 0.0,
    anchor_object: Literal["auto", "left", "right"] = "auto",
    tolerance: float = 0.0001,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for placing or correcting one mirrored pair.

    Use this when two existing parts should form a mirrored pair around one
    explicit mirror plane. The first slice:

    - works on one existing pair only
    - chooses an anchor (`left`, `right`, or `auto`)
    - mirrors the follower object's center across `axis + mirror_coordinate`
    - verifies the result with `scene_assert_symmetry`

    It does not yet try to solve contact-to-body placement or dimension
    rescaling; those remain separate concerns from this pair-symmetry tool.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            payload = get_macro_handler().place_symmetry_pair(
                left_object=left_object,
                right_object=right_object,
                axis=axis,
                mirror_coordinate=mirror_coordinate,
                anchor_object=anchor_object,
                tolerance=tolerance,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_place_symmetry_pair",
                intent=f"place symmetry pair '{left_object}' / '{right_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_place_symmetry_pair",
        params={
            "left_object": left_object,
            "right_object": right_object,
            "axis": axis,
            "mirror_coordinate": mirror_coordinate,
            "anchor_object": anchor_object,
            "tolerance": tolerance,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_place_symmetry_pair",
        intent=f"place symmetry pair '{left_object}' / '{right_object}'",
    )


async def macro_place_supported_pair(
    ctx: Context,
    left_object: str,
    right_object: str,
    support_object: str,
    axis: Literal["X", "Y", "Z"] = "X",
    mirror_coordinate: float = 0.0,
    support_axis: Literal["X", "Y", "Z"] = "Z",
    support_side: Literal["positive", "negative"] = "positive",
    anchor_object: Literal["auto", "left", "right"] = "auto",
    gap: float = 0.0,
    tolerance: float = 0.0001,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for placing or correcting one mirrored pair against a shared support surface.

    Use this when two existing objects should stay mirrored around one explicit
    plane while both making bounded contact with the same support object. The
    first slice:

    - works on one existing pair plus one existing support object
    - keeps mirror placement and support contact as separate explicit constraints
    - blocks when those constraints would require materially different support coordinates
    - does not enter rigging, pose mode, or multi-joint articulation
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            payload = get_macro_handler().place_supported_pair(
                left_object=left_object,
                right_object=right_object,
                support_object=support_object,
                axis=axis,
                mirror_coordinate=mirror_coordinate,
                support_axis=support_axis,
                support_side=support_side,
                anchor_object=anchor_object,
                gap=gap,
                tolerance=tolerance,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_place_supported_pair",
                intent=f"place supported pair '{left_object}' / '{right_object}' on '{support_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_place_supported_pair",
        params={
            "left_object": left_object,
            "right_object": right_object,
            "support_object": support_object,
            "axis": axis,
            "mirror_coordinate": mirror_coordinate,
            "support_axis": support_axis,
            "support_side": support_side,
            "anchor_object": anchor_object,
            "gap": gap,
            "tolerance": tolerance,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_place_supported_pair",
        intent=f"place supported pair '{left_object}' / '{right_object}' on '{support_object}'",
    )


async def macro_cleanup_part_intersections(
    ctx: Context,
    part_object: str,
    reference_object: str,
    gap: float = 0.0,
    normal_axis: Literal["X", "Y", "Z"] | None = None,
    preserve_side: bool = True,
    max_push: float = 0.5,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for resolving one obvious overlap between two existing objects.

    Use this when one part is visibly intersecting another and the intended fix
    is a bounded push out to contact or a small gap, not an unconstrained
    rebuild or physics/collision solve.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            payload = get_macro_handler().cleanup_part_intersections(
                part_object=part_object,
                reference_object=reference_object,
                gap=gap,
                normal_axis=normal_axis,
                preserve_side=preserve_side,
                max_push=max_push,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_cleanup_part_intersections",
                intent=f"clean intersection between '{part_object}' and '{reference_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_cleanup_part_intersections",
        params={
            "part_object": part_object,
            "reference_object": reference_object,
            "gap": gap,
            "normal_axis": normal_axis,
            "preserve_side": preserve_side,
            "max_push": max_push,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_cleanup_part_intersections",
        intent=f"clean intersection between '{part_object}' and '{reference_object}'",
    )


async def macro_adjust_relative_proportion(
    ctx: Context,
    primary_object: str,
    reference_object: str,
    expected_ratio: float,
    primary_axis: Literal["X", "Y", "Z"] = "X",
    reference_axis: Literal["X", "Y", "Z"] = "X",
    scale_target: Literal["primary", "reference"] = "primary",
    tolerance: float = 0.01,
    uniform_scale: bool = True,
    max_scale_delta: float = 0.5,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for repairing relative proportion drift between two objects.

    Use this when the current cross-object ratio is visibly off but the pair is
    already otherwise useful enough that a bounded scale repair is safer than a
    rebuild or open-ended sculpt pass.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            payload = get_macro_handler().adjust_relative_proportion(
                primary_object=primary_object,
                reference_object=reference_object,
                expected_ratio=expected_ratio,
                primary_axis=primary_axis,
                reference_axis=reference_axis,
                scale_target=scale_target,
                tolerance=tolerance,
                uniform_scale=uniform_scale,
                max_scale_delta=max_scale_delta,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_adjust_relative_proportion",
                intent=f"repair relative proportion for '{primary_object}' relative to '{reference_object}'",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_adjust_relative_proportion",
        params={
            "primary_object": primary_object,
            "reference_object": reference_object,
            "expected_ratio": expected_ratio,
            "primary_axis": primary_axis,
            "reference_axis": reference_axis,
            "scale_target": scale_target,
            "tolerance": tolerance,
            "uniform_scale": uniform_scale,
            "max_scale_delta": max_scale_delta,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_adjust_relative_proportion",
        intent=f"repair relative proportion for '{primary_object}' relative to '{reference_object}'",
    )


async def macro_adjust_segment_chain_arc(
    ctx: Context,
    segment_objects: List[str],
    rotation_axis: Literal["X", "Y", "Z"] = "Y",
    total_angle: float = 30.0,
    direction: Literal["positive", "negative"] = "positive",
    segment_spacing: float | None = None,
    apply_rotation: bool = True,
) -> MacroExecutionReportContract:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Bounded macro for adjusting an ordered segment chain into a cleaner planar arc.

    Use this when an ordered chain of existing segment objects needs a cleaner
    planar arc without resorting to free-form tool chaining or rigging.
    """

    capture_profile = await _resolve_macro_capture_profile(ctx)

    def execute() -> MacroExecutionReportContract:
        try:
            payload = get_macro_handler().adjust_segment_chain_arc(
                segment_objects=segment_objects,
                rotation_axis=rotation_axis,
                total_angle=total_angle,
                direction=direction,
                segment_spacing=segment_spacing,
                apply_rotation=apply_rotation,
                capture_profile=capture_profile,
            )
            return MacroExecutionReportContract.model_validate(payload)
        except (RuntimeError, ValueError) as e:
            return MacroExecutionReportContract(
                status="failed",
                macro_name="macro_adjust_segment_chain_arc",
                intent=f"adjust segment chain arc for {len(segment_objects)} segment(s)",
                actions_taken=[],
                requires_followup=False,
                error=str(e),
            )

    result = await route_tool_call_async(
        ctx,
        tool_name="macro_adjust_segment_chain_arc",
        params={
            "segment_objects": segment_objects,
            "rotation_axis": rotation_axis,
            "total_angle": total_angle,
            "direction": direction,
            "segment_spacing": segment_spacing,
            "apply_rotation": apply_rotation,
        },
        direct_executor=execute,
    )
    return await _finalize_macro_execution_result(
        ctx,
        result,
        macro_name="macro_adjust_segment_chain_arc",
        intent=f"adjust segment chain arc for {len(segment_objects)} segment(s)",
    )


async def _maybe_attach_scene_inspection_assistant(
    ctx: Context,
    contract: SceneInspectResponseContract,
    *,
    object_name: str | None,
) -> SceneInspectResponseContract:
    """Attach a bounded assistant summary to a scene inspection response."""

    if contract.error:
        return contract

    outcome = await run_inspection_summary_assistant(
        ctx,
        action=contract.action,
        object_name=object_name,
        payload=contract.model_dump(exclude_none=True),
    )
    return contract.model_copy(update={"assistant": to_inspection_assistant_contract(outcome)})


async def _maybe_attach_scene_state_assistant(
    ctx: Context,
    contract,
    *,
    subject: str,
    object_name: str | None = None,
):
    """Attach a bounded assistant summary to a structured scene-state contract."""

    if getattr(contract, "error", None):
        return contract

    outcome = await run_inspection_summary_assistant(
        ctx,
        action=subject,
        object_name=object_name,
        payload=contract.model_dump(exclude_none=True),
    )
    return contract.model_copy(update={"assistant": to_inspection_assistant_contract(outcome)})


# ... Scene Tools ...
def scene_list_objects(ctx: Context) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Lists all objects in the current Blender scene with their types.

    Workflow: READ-ONLY | START → understand scene
    """

    return route_scene_list_objects(
        ctx,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_delete_object(name: str, ctx: Context) -> str:
    """
    [SCENE][DESTRUCTIVE] Deletes an object from the scene by name.
    This permanently removes the object.

    Workflow: DESTRUCTIVE | BEFORE → scene_list_objects

    Args:
        name: Name of the object to delete.
    """
    return route_scene_delete_object(
        name,
        ctx,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


def scene_clean_scene(
    ctx: Context,
    keep_lights_and_cameras: bool | None = None,
    keep_lights: bool | None = None,
    keep_cameras: bool | None = None,
) -> str:
    """
    [SCENE][DESTRUCTIVE] Deletes objects from the scene.
    WARNING: If keep_lights_and_cameras=False, deletes EVERYTHING (hard reset).

    Workflow: START → fresh scene | AFTER → modeling_create_primitive

    Args:
        keep_lights_and_cameras: Canonical public cleanup flag. If True (default),
            keeps Lights and Cameras. If False, deletes EVERYTHING (hard reset).
        keep_lights: Legacy compatibility-only split flag. Use only when it
            matches `keep_cameras`.
        keep_cameras: Legacy compatibility-only split flag. Use only when it
            matches `keep_lights`.
    """
    return route_scene_clean_scene(
        ctx,
        keep_lights_and_cameras=keep_lights_and_cameras,
        keep_lights=keep_lights,
        keep_cameras=keep_cameras,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


async def _scene_clean_scene_async(
    ctx: Context,
    keep_lights_and_cameras: bool | None = None,
    keep_lights: bool | None = None,
    keep_cameras: bool | None = None,
) -> str:
    """Async registered variant that awaits guided session updates on Streamable HTTP."""

    return await route_scene_clean_scene_async(
        ctx,
        keep_lights_and_cameras=keep_lights_and_cameras,
        keep_lights=keep_lights,
        keep_cameras=keep_cameras,
        get_scene_handler_fn=get_scene_handler,
        hydrate_sync_route_session_fn=_hydrate_sync_route_session,
        route_tool_call_report_for_context_fn=_route_tool_call_report_for_context,
        legacy_route_report_result_fn=_legacy_route_report_result,
        report_has_successful_scene_clean_step_fn=_report_has_successful_scene_clean_step,
        mark_guided_spatial_state_stale_async_fn=mark_guided_spatial_state_stale_async,
        to_thread_fn=asyncio.to_thread,
    )


def scene_duplicate_object(ctx: Context, name: str, translation: Union[str, List[float], None] = None) -> str:
    """
    [SCENE][SAFE] Duplicates an object and optionally moves it.

    Workflow: AFTER → scene_set_active | USE FOR → copies with offset

    Args:
        name: Name of the object to duplicate.
        translation: Optional [x, y, z] vector to move the copy. Can be a list or string '[1.0, 2.0, 3.0]'.
    """

    return route_scene_duplicate_object(
        ctx,
        name=name,
        translation=translation,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        parse_coordinate_fn=parse_coordinate,
    )


def scene_set_active_object(ctx: Context, name: str) -> str:
    """
    [SCENE][SAFE] Sets the active object.
    Important for operations that work on the "active" object (like adding modifiers).

    Workflow: BEFORE → any object operation | REQUIRED BY → modifiers, transforms

    Args:
        name: Name of the object to set as active.
    """
    return route_scene_set_active_object(
        ctx,
        name=name,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


def scene_context(ctx: Context, action: Literal["mode", "selection"]) -> SceneContextResponseContract:
    """
    [SCENE][READ-ONLY][SAFE] Quick context queries for scene state.

    Actions:
    - "mode": Returns current Blender mode, active object, selection count.
    - "selection": Returns selected objects list + edit mode vertex/edge/face counts.

    Workflow: READ-ONLY | FIRST STEP → check context before any operation

    Examples:
        scene_context(action="mode")
        scene_context(action="selection")
    """

    def execute():
        return execute_scene_context(
            ctx=ctx,
            action=action,
            read_mode=_scene_get_mode,
            read_selection=_scene_list_selection,
        )

    return route_tool_call(tool_name="scene_context", params={"action": action}, direct_executor=execute)


# Internal function - exposed via scene_context mega tool
def _scene_get_mode(ctx: Context) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Reports the current Blender interaction mode and selection summary.

    Workflow: READ-ONLY | USE → check context before operations

    Returns a multi-line description with mode, active object, and selected objects to help
    AI agents branch logic without guessing the context.
    """
    return _scene_get_mode_impl(ctx=ctx, get_scene_handler=get_scene_handler)


# Internal function - exposed via scene_context mega tool
def _scene_list_selection(ctx: Context) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Lists the current selection in Object or Edit Mode.

    Workflow: READ-ONLY | USE → verify selection state

    Provides counts for selected objects and, when in Edit Mode, counts of selected
    vertices/edges/faces. Useful for verifying assumptions before destructive edits.
    """
    return _scene_list_selection_impl(ctx=ctx, get_scene_handler=get_scene_handler)


async def scene_inspect(
    ctx: Context,
    action: Literal[
        "object",
        "topology",
        "modifiers",
        "materials",
        "constraints",
        "modifier_data",
        "render",
        "color_management",
        "world",
    ],
    object_name: Optional[str] = None,
    detailed: bool = False,
    include_disabled: bool = True,
    material_filter: Optional[str] = None,
    include_empty_slots: bool = True,
    include_bones: bool = False,
    modifier_name: Optional[str] = None,
    include_node_tree: bool = False,
    assistant_summary: bool = False,
) -> SceneInspectResponseContract:
    """
    [SCENE][READ-ONLY][SAFE] Detailed inspection queries for objects and scene.

    Actions and required parameters:
    - "object": Requires object_name. Returns transform, collections, materials, modifiers, mesh stats.
    - "topology": Requires object_name. Returns vertex/edge/face/tri/quad/ngon counts. Optional: detailed=True for non-manifold checks.
    - "modifiers": Optional object_name (None scans all). Returns modifier stacks. Optional: include_disabled=False.
    - "materials": No params required. Returns material slot audit. Optional: material_filter, include_empty_slots.
    - "constraints": Requires object_name. Returns object (and optional bone) constraints.
    - "modifier_data": Requires object_name. Returns full modifier properties (optional modifier_name, include_node_tree).
    - "render": No params required. Returns render-engine/output/resolution settings.
    - "color_management": No params required. Returns display/view/sequencer color-management settings.
    - "world": No params required. Returns active world/background state and node summary when available.
    - assistant_summary: Optional bounded server-side summary of the structured inspection payload.

    Workflow: READ-ONLY | USE → detailed analysis before export or debugging

    Examples:
        scene_inspect(action="object", object_name="Cube")
        scene_inspect(action="topology", object_name="Cube", detailed=True)
        scene_inspect(action="modifiers", object_name="Cube")
        scene_inspect(action="modifiers")  # scans all objects
        scene_inspect(action="materials", material_filter="Wood")
        scene_inspect(action="constraints", object_name="Rig", include_bones=True)
        scene_inspect(action="modifier_data", object_name="Cube", modifier_name="Bevel")
        scene_inspect(action="render")
        scene_inspect(action="color_management")
        scene_inspect(action="world")
    """

    def execute():
        return execute_scene_inspect(
            ctx=ctx,
            action=action,
            object_name=object_name,
            detailed=detailed,
            include_disabled=include_disabled,
            material_filter=material_filter,
            include_empty_slots=include_empty_slots,
            include_bones=include_bones,
            modifier_name=modifier_name,
            include_node_tree=include_node_tree,
            inspect_object=_scene_inspect_object,
            inspect_topology=_scene_inspect_mesh_topology,
            inspect_modifiers=_scene_inspect_modifiers,
            inspect_materials=_scene_inspect_material_slots,
            inspect_constraints=_scene_get_constraints,
            inspect_modifier_data=_scene_inspect_modifier_data,
            inspect_render=_scene_inspect_render_settings,
            inspect_color_management=_scene_inspect_color_management,
            inspect_world=_scene_inspect_world,
        )

    result = route_tool_call(
        tool_name="scene_inspect",
        params={
            "action": action,
            "object_name": object_name,
            "detailed": detailed,
            "include_disabled": include_disabled,
            "material_filter": material_filter,
            "include_empty_slots": include_empty_slots,
            "include_bones": include_bones,
            "modifier_name": modifier_name,
            "include_node_tree": include_node_tree,
            "assistant_summary": assistant_summary,
        },
        direct_executor=execute,
    )
    if not isinstance(result, SceneInspectResponseContract):
        return SceneInspectResponseContract(action=action, error=str(result))
    if not assistant_summary:
        return result
    return await _maybe_attach_scene_inspection_assistant(
        ctx,
        result,
        object_name=object_name,
    )


def scene_configure(
    ctx: Context,
    action: Literal["render", "color_management", "world"],
    settings: Dict[str, Any],
) -> SceneConfigureResponseContract:
    """
    [SCENE][NON-DESTRUCTIVE] Applies grouped scene-level render, color-management, or world configuration.

    Actions and settings shape:
    - "render": Accepts fields aligned with `scene_inspect(action="render")`, including render_engine,
      resolution, filepath, use_file_extension, film_transparent, image_settings, and cycles.
    - "color_management": Accepts fields aligned with `scene_inspect(action="color_management")`,
      including display_device, view_transform, look, exposure, gamma, use_curve_mapping, and
      sequencer_color_space.
    - "world": Accepts grouped world/background settings such as world_name, use_nodes, color,
      and background {color, strength}. This tool does not author arbitrary world node graphs.

    Workflow: NON-DESTRUCTIVE | USE → replay scene appearance from structured state

    Examples:
        scene_configure(action="render", settings={"render_engine": "CYCLES", "cycles": {"samples": 128}})
        scene_configure(action="color_management", settings={"view_transform": "AgX", "look": "None"})
        scene_configure(action="world", settings={"world_name": "Studio", "background": {"strength": 0.8}})
    """

    def execute() -> SceneConfigureResponseContract:
        return execute_scene_configure(
            ctx=ctx,
            action=action,
            settings=settings,
            configure_render=_scene_configure_render_settings,
            configure_color_management=_scene_configure_color_management,
            configure_world=_scene_configure_world,
        )

    result = route_tool_call(
        tool_name="scene_configure",
        params={"action": action, "settings": settings},
        direct_executor=execute,
    )
    if isinstance(result, SceneConfigureResponseContract):
        return result
    if isinstance(result, dict):
        if "error" in result and result.get("payload") is None:
            return SceneConfigureResponseContract(action=action, error=str(result["error"]))
        return SceneConfigureResponseContract(action=action, payload=result)
    return SceneConfigureResponseContract(action=action, error=str(result))


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_object(ctx: Context, name: str) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Provides a detailed report for a single object (transform, collections, materials, modifiers, mesh stats).

    Workflow: READ-ONLY | USE → detailed object audit
    """
    return _scene_inspect_object_impl(ctx=ctx, name=name, get_scene_handler=get_scene_handler)


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_render_settings(ctx: Context) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Returns structured render settings for the active scene.

    Workflow: READ-ONLY | USE → capture scene-level render configuration
    """
    return _scene_inspect_render_settings_impl(ctx=ctx, get_scene_handler=get_scene_handler)


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_color_management(ctx: Context) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Returns structured color-management settings for the active scene.

    Workflow: READ-ONLY | USE → capture scene appearance/display configuration
    """
    return _scene_inspect_color_management_impl(ctx=ctx, get_scene_handler=get_scene_handler)


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_world(ctx: Context) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Returns structured world/background settings for the active scene.

    Workflow: READ-ONLY | USE → inspect scene background and world configuration
    """
    return _scene_inspect_world_impl(ctx=ctx, get_scene_handler=get_scene_handler)


def _scene_configure_render_settings(ctx: Context, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    [SCENE][NON-DESTRUCTIVE] Applies grouped render settings and returns the resulting render snapshot.
    """
    return execute_scene_configure_render_settings(ctx=ctx, settings=settings, handler_getter=get_scene_handler)


def _scene_configure_color_management(ctx: Context, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    [SCENE][NON-DESTRUCTIVE] Applies grouped color-management settings and returns the resulting snapshot.
    """
    return execute_scene_configure_color_management(ctx=ctx, settings=settings, handler_getter=get_scene_handler)


def _scene_configure_world(ctx: Context, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    [SCENE][NON-DESTRUCTIVE] Applies grouped world/background settings and returns the resulting world snapshot.
    """
    return execute_scene_configure_world(ctx=ctx, settings=settings, handler_getter=get_scene_handler)


def _format_viewport_output(
    b64_data: str,
    *,
    width: int,
    height: int,
    shading: str,
    output_mode: str | None,
) -> Union[Image, str]:
    """Format a base64 viewport payload into the requested MCP delivery shape."""
    return _format_viewport_output_impl(
        b64_data,
        width=width,
        height=height,
        shading=shading,
        output_mode=output_mode,
    )


async def scene_get_viewport(
    ctx: Context,
    width: int = 1024,
    height: int = 768,
    shading: str = "SOLID",
    camera_name: str = None,
    focus_target: str = None,
    view_name: str = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float = None,
    persist_view: bool = False,
    output_mode: Literal["IMAGE", "BASE64", "FILE", "MARKDOWN"] = "IMAGE",
) -> Union[Image, str]:
    """Get a visual preview of the scene (OpenGL Viewport Render).

    Workflow: LAST STEP → visual verification | USE → AI preview

    The tool can return the viewport in multiple formats, controlled by
    ``output_mode``:

    * ``IMAGE`` (default): Returns a FastMCP ``Image`` resource (best for
      clients that natively support image resources, like Cline).
    * ``BASE64``: Returns the raw base64-encoded JPEG data as a string for
      direct consumption by Vision modules.
    * ``FILE``: Saves the image to a temp directory and returns a description
      containing **host-visible** file paths, without markdown or data URLs.
    * ``MARKDOWN``: Saves the image to a temp directory and returns rich
      markdown with an inline ``data:`` URL preview plus host-visible paths.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        shading: Viewport shading mode ('WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED').
        camera_name: Name of the camera to use. If None or "USER_PERSPECTIVE", uses a temporary
            camera.
        focus_target: Name of the object to focus on. Only works if camera_name is
            None/"USER_PERSPECTIVE".
        view_name: Optional standard user-view preset ('FRONT', 'RIGHT', 'TOP') applied
            before capture when using USER_PERSPECTIVE.
        orbit_horizontal: Optional horizontal orbit in degrees applied to USER_PERSPECTIVE before capture.
        orbit_vertical: Optional vertical orbit in degrees applied to USER_PERSPECTIVE before capture.
        zoom_factor: Optional user-view zoom factor applied with focus_target or current USER_PERSPECTIVE view.
        persist_view: If True, keeps the adjusted USER_PERSPECTIVE after capture. Defaults to False.
        output_mode: Output format selector: "IMAGE", "BASE64", "FILE", or "MARKDOWN".
    """
    return await _route_scene_get_viewport(
        ctx,
        width=width,
        height=height,
        shading=shading,
        camera_name=camera_name,
        focus_target=focus_target,
        view_name=view_name,
        orbit_horizontal=orbit_horizontal,
        orbit_vertical=orbit_vertical,
        zoom_factor=zoom_factor,
        persist_view=persist_view,
        output_mode=output_mode,
        get_scene_handler_fn=get_scene_handler,
        is_background_task_context_fn=is_background_task_context,
        run_rpc_background_job_fn=run_rpc_background_job,
        route_tool_call_fn=route_tool_call,
        format_viewport_output_fn=_format_viewport_output,
    )


async def scene_snapshot_state(
    ctx: Context,
    include_mesh_stats: bool = False,
    include_materials: bool = False,
    assistant_summary: bool = False,
) -> SceneSnapshotStateContract:
    """
    [SCENE][SAFE][READ-ONLY] Captures a lightweight JSON snapshot of the scene state.

    Workflow: BEFORE → operations | AFTER → scene_compare_snapshot

    Returns a serialized snapshot containing object transforms, hierarchy, modifiers,
    and selection state. Includes a SHA256 hash for change detection. Large payloads
    are possible when optional flags are enabled.

    Args:
        include_mesh_stats: If True, includes vertex/edge/face counts for mesh objects.
        include_materials: If True, includes material names assigned to objects.
        assistant_summary: If True, attaches a bounded assistant summary for the snapshot payload.
    """

    def execute():
        return execute_scene_snapshot_state(
            ctx=ctx,
            include_mesh_stats=include_mesh_stats,
            include_materials=include_materials,
            get_scene_handler=get_scene_handler,
            info=ctx_info,
        )

    result = route_tool_call(
        tool_name="scene_snapshot_state",
        params={
            "include_mesh_stats": include_mesh_stats,
            "include_materials": include_materials,
            "assistant_summary": assistant_summary,
        },
        direct_executor=execute,
    )
    if not isinstance(result, SceneSnapshotStateContract):
        return SceneSnapshotStateContract(error=str(result))
    if not assistant_summary:
        return result
    return await _maybe_attach_scene_state_assistant(ctx, result, subject="scene_snapshot_state")


async def scene_compare_snapshot(
    ctx: Context,
    baseline_snapshot: str,
    target_snapshot: str,
    ignore_minor_transforms: float = 0.0,
    assistant_summary: bool = False,
) -> SceneSnapshotDiffContract:
    """
    [SCENE][SAFE][READ-ONLY] Compares two scene snapshots and returns a diff summary.

    Workflow: AFTER → scene_snapshot_state (x2) | USE → verify changes

    Takes two JSON snapshot strings (from scene_snapshot_state) and computes
    the differences: objects added/removed, and modifications to transforms,
    modifiers, and materials.

    Args:
        baseline_snapshot: JSON string of the baseline snapshot
        target_snapshot: JSON string of the target snapshot
        ignore_minor_transforms: Threshold for ignoring small transform changes (default 0.0)
        assistant_summary: If True, attaches a bounded assistant summary for the diff payload.
    """

    def execute():
        return execute_scene_compare_snapshot(
            ctx=ctx,
            baseline_snapshot=baseline_snapshot,
            target_snapshot=target_snapshot,
            ignore_minor_transforms=ignore_minor_transforms,
            get_snapshot_diff_service=get_snapshot_diff_service,
            info=ctx_info,
        )

    result = route_tool_call(
        tool_name="scene_compare_snapshot",
        params={
            "baseline_snapshot": baseline_snapshot,
            "target_snapshot": target_snapshot,
            "ignore_minor_transforms": ignore_minor_transforms,
            "assistant_summary": assistant_summary,
        },
        direct_executor=execute,
    )
    if not isinstance(result, SceneSnapshotDiffContract):
        return SceneSnapshotDiffContract(error=str(result))
    if not assistant_summary:
        return result
    return await _maybe_attach_scene_state_assistant(ctx, result, subject="scene_compare_snapshot")


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_material_slots(
    ctx: Context, material_filter: Optional[str] = None, include_empty_slots: bool = True
) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Audits material slot assignments across the entire scene.

    Workflow: READ-ONLY | USE WITH → material_list_by_object

    Provides a comprehensive view of how materials are distributed across all objects,
    including empty slots, missing materials, and assignment statistics. Useful for
    identifying material issues before rendering or export.

    Args:
        material_filter: Optional material name to filter results
        include_empty_slots: If True, includes slots with no material assigned
    """
    return _scene_inspect_material_slots_impl(
        ctx=ctx,
        material_filter=material_filter,
        include_empty_slots=include_empty_slots,
        get_scene_handler=get_scene_handler,
        info=ctx_info,
    )


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_mesh_topology(ctx: Context, object_name: str, detailed: bool = False) -> Dict[str, Any]:
    """
    [MESH][SAFE][READ-ONLY] Reports detailed topology stats for a given mesh.

    Workflow: READ-ONLY | USE → quality check before export

    Includes counts for vertices, edges, faces, triangles, quads, ngons.
    If detailed=True, checks for non-manifold edges and loose geometry (more expensive).

    Args:
        object_name: Name of the mesh object.
        detailed: If True, performs expensive checks (non-manifold, loose geometry).
    """
    return _scene_inspect_mesh_topology_impl(
        ctx=ctx,
        object_name=object_name,
        detailed=detailed,
        get_scene_handler=get_scene_handler,
    )


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_modifiers(
    ctx: Context, object_name: Optional[str] = None, include_disabled: bool = True
) -> Dict[str, Any]:
    """
    [SCENE][SAFE][READ-ONLY] Lists modifier stacks with key settings.

    Workflow: READ-ONLY | BEFORE → modeling_apply_modifier

    Can inspect a specific object or audit the entire scene.

    Args:
        object_name: Optional name of the object to inspect. If None, scans all objects.
        include_disabled: If True, includes modifiers disabled in viewport/render.
    """
    return _scene_inspect_modifiers_impl(
        ctx=ctx,
        object_name=object_name,
        include_disabled=include_disabled,
        get_scene_handler=get_scene_handler,
        info=ctx_info,
    )


# Internal function - exposed via scene_inspect mega tool
def _scene_get_constraints(ctx: Context, object_name: str, include_bones: bool = False) -> Dict[str, Any]:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns object (and optional bone) constraints.
    """
    return _scene_get_constraints_impl(
        ctx=ctx,
        object_name=object_name,
        include_bones=include_bones,
        get_scene_handler=get_scene_handler,
    )


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_modifier_data(
    ctx: Context, object_name: str, modifier_name: Optional[str] = None, include_node_tree: bool = False
) -> Dict[str, Any]:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns full modifier properties.
    """
    from server.adapters.mcp.areas.modeling import _modeling_get_modifier_data

    return _scene_inspect_modifier_data_impl(
        ctx=ctx,
        object_name=object_name,
        modifier_name=modifier_name,
        include_node_tree=include_node_tree,
        modeling_get_modifier_data=_modeling_get_modifier_data,
    )


def scene_create(
    ctx: Context,
    action: Literal["light", "camera", "empty"],
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    rotation: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: Optional[str] = None,
    # Light params:
    light_type: Literal["POINT", "SUN", "SPOT", "AREA"] = "POINT",
    energy: float = 1000.0,
    color: Union[str, List[float]] = [1.0, 1.0, 1.0],
    # Camera params:
    lens: float = 50.0,
    clip_start: Optional[float] = None,
    clip_end: Optional[float] = None,
    # Empty params:
    empty_type: Literal[
        "PLAIN_AXES", "ARROWS", "SINGLE_ARROW", "CIRCLE", "CUBE", "SPHERE", "CONE", "IMAGE"
    ] = "PLAIN_AXES",
    size: float = 1.0,
) -> SceneCreateResponseContract:
    """
    [SCENE][SAFE] Creates scene helper objects (lights, cameras, empties).

    Actions and parameters:
    - "light": Creates light source. Optional: light_type (POINT/SUN/SPOT/AREA), energy, color, location, name.
    - "camera": Creates camera. Optional: location, rotation, lens, clip_start, clip_end, name.
    - "empty": Creates empty object. Optional: empty_type (PLAIN_AXES/ARROWS/CIRCLE/CUBE/SPHERE/CONE/IMAGE), size, location, name.

    All location/rotation/color params accept either list [x,y,z] or string "[x,y,z]".

    For mesh primitives (Cube, Sphere, etc.) use modeling_create_primitive instead.

    Workflow: AFTER → geometry complete | BEFORE → scene_get_viewport

    Examples:
        scene_create(action="light", light_type="SUN", energy=5.0)
        scene_create(action="light", light_type="AREA", location=[0, 0, 5], color=[1.0, 0.9, 0.8])
        scene_create(action="camera", location=[0, -10, 5], rotation=[1.0, 0, 0])
        scene_create(action="empty", empty_type="ARROWS", location=[0, 0, 2])
    """

    def execute() -> SceneCreateResponseContract:
        return execute_scene_create(
            ctx=ctx,
            action=action,
            location=location,
            rotation=rotation,
            name=name,
            light_type=light_type,
            energy=energy,
            color=color,
            lens=lens,
            clip_start=clip_start,
            clip_end=clip_end,
            empty_type=empty_type,
            size=size,
            parse_coordinate=parse_coordinate,
            create_light=_scene_create_light,
            create_camera=_scene_create_camera,
            create_empty=_scene_create_empty,
        )

    result = route_tool_call(
        tool_name="scene_create",
        params={
            "action": action,
            "location": location,
            "rotation": rotation,
            "name": name,
            "light_type": light_type,
            "energy": energy,
            "color": color,
            "lens": lens,
            "clip_start": clip_start,
            "clip_end": clip_end,
            "empty_type": empty_type,
            "size": size,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneCreateResponseContract):
        return result
    if isinstance(result, dict):
        if "error" in result and result.get("payload") is None:
            return SceneCreateResponseContract(action=action, error=str(result["error"]))
        return SceneCreateResponseContract(action=action, payload=result)
    return SceneCreateResponseContract(action=action, error=str(result))


# Internal function - exposed via scene_create mega tool
def _scene_create_light(
    ctx: Context,
    type: str,
    energy: float = 1000.0,
    color: Union[str, List[float]] = [1.0, 1.0, 1.0],
    location: Union[str, List[float]] = [0.0, 0.0, 5.0],
    name: Optional[str] = None,
) -> str:
    """
    [SCENE][SAFE] Creates a light source.

    Workflow: AFTER → geometry complete | BEFORE → scene_get_viewport

    Args:
        type: 'POINT', 'SUN', 'SPOT', 'AREA'.
        energy: Power in Watts.
        color: [r, g, b] (0.0 to 1.0). Can be a list or string '[1.0, 1.0, 1.0]'.
        location: [x, y, z]. Can be a list or string.
        name: Optional custom name.
    """
    try:
        parsed_color = parse_coordinate(color) or [1.0, 1.0, 1.0]
        parsed_location = parse_coordinate(location) or [0.0, 0.0, 5.0]
        return execute_scene_create_light(
            ctx=ctx,
            handler_getter=get_scene_handler,
            type=type,
            energy=energy,
            color=parsed_color,
            location=parsed_location,
            name=name,
        )
    except (RuntimeError, ValueError) as e:
        return str(e)


# Internal function - exposed via scene_create mega tool
def _scene_create_camera(
    ctx: Context,
    location: Union[str, List[float]],
    rotation: Union[str, List[float]],
    lens: float = 50.0,
    clip_start: Optional[float] = None,
    clip_end: Optional[float] = None,
    name: Optional[str] = None,
) -> str:
    """
    [SCENE][SAFE] Creates a camera object.

    Workflow: AFTER → geometry complete | USE WITH → scene_get_viewport

    Args:
        location: [x, y, z]. Can be a list or string '[0.0, 0.0, 10.0]'.
        rotation: [x, y, z] Euler angles in radians. Can be a list or string.
        lens: Focal length in mm.
        clip_start: Near clipping distance.
        clip_end: Far clipping distance.
        name: Optional custom name.
    """
    try:
        parsed_location = parse_coordinate(location)
        parsed_rotation = parse_coordinate(rotation)
        if parsed_location is None or parsed_rotation is None:
            return "Invalid location or rotation coordinate payload."
        return execute_scene_create_camera(
            ctx=ctx,
            handler_getter=get_scene_handler,
            location=parsed_location,
            rotation=parsed_rotation,
            lens=lens,
            clip_start=clip_start,
            clip_end=clip_end,
            name=name,
        )
    except (RuntimeError, ValueError) as e:
        return str(e)


# Internal function - exposed via scene_create mega tool
def _scene_create_empty(
    ctx: Context,
    type: str,
    size: float = 1.0,
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: Optional[str] = None,
) -> str:
    """
    [SCENE][SAFE] Creates an Empty object (useful for grouping or tracking).

    Workflow: USE FOR → grouping/parenting | WITH → scene_set_active

    Args:
        type: 'PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE', 'IMAGE'.
        size: Display size.
        location: [x, y, z]. Can be a list or string '[0.0, 0.0, 0.0]'.
        name: Optional custom name.
    """
    try:
        parsed_location = parse_coordinate(location) or [0.0, 0.0, 0.0]
        return execute_scene_create_empty(
            ctx=ctx,
            handler_getter=get_scene_handler,
            type=type,
            size=size,
            location=parsed_location,
            name=name,
        )
    except (RuntimeError, ValueError) as e:
        return str(e)


def scene_set_mode(ctx: Context, mode: str) -> str:
    """
    [SCENE][SAFE] Sets the interaction mode (OBJECT, EDIT, SCULPT, POSE, WEIGHT_PAINT, TEXTURE_PAINT).

    Workflow: CRITICAL → switching OBJECT↔EDIT | BEFORE → mesh_* or modeling_*

    Args:
        mode: The target mode (case-insensitive).
    """

    return route_scene_set_mode(
        ctx,
        mode=mode,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


# TASK-043: Scene Utility Tools


def scene_rename_object(ctx: Context, old_name: str, new_name: str) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Renames an object in the scene.

    Workflow: AFTER → scene_list_objects | USE FOR → organizing imported models

    Args:
        old_name: Current name of the object
        new_name: New name for the object

    Returns:
        Success message with old and new name, or error if object not found
    """

    return route_scene_rename_object(
        ctx,
        old_name=old_name,
        new_name=new_name,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


def scene_hide_object(ctx: Context, object_name: str, hide: bool = True, hide_render: bool = False) -> str:
    """
    [OBJECT MODE][SCENE][NON-DESTRUCTIVE] Hides or shows an object.

    Workflow: USE FOR → isolating components, cleaning viewport

    Args:
        object_name: Name of the object to hide/show
        hide: True to hide in viewport, False to show
        hide_render: If True while hiding, also hide in renders. Showing an object restores
            render visibility as well.

    Returns:
        Success message with visibility state
    """

    return route_scene_hide_object(
        ctx,
        object_name=object_name,
        hide=hide,
        hide_render=hide_render,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


def scene_show_all_objects(ctx: Context, include_render: bool = False) -> str:
    """
    [OBJECT MODE][SCENE][NON-DESTRUCTIVE] Shows all hidden objects.

    Workflow: AFTER → scene_hide_object | USE FOR → resetting visibility

    Args:
        include_render: If True, also restore render visibility for objects hidden from renders

    Returns:
        Count of objects made visible
    """

    return route_scene_show_all_objects(
        ctx,
        include_render=include_render,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


def scene_isolate_object(ctx: Context, object_name: Union[str, List[str]]) -> str:
    """
    [OBJECT MODE][SCENE][NON-DESTRUCTIVE] Isolates object(s) by hiding all others.

    Workflow: USE FOR → focused inspection of specific component

    Args:
        object_name: Name or list of names to keep visible. Non-target objects are hidden
            in both viewport and render so named-camera captures match the isolated set.

    Returns:
        Count of objects hidden
    """

    return route_scene_isolate_object(
        ctx,
        object_name=object_name,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


def scene_camera_orbit(
    ctx: Context,
    angle_horizontal: float = 0.0,
    angle_vertical: float = 0.0,
    target_object: Optional[str] = None,
    target_point: Union[str, List[float], None] = None,
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Orbits viewport camera around target.

    Workflow: USE FOR → inspecting object from different angles

    Args:
        angle_horizontal: Horizontal rotation in degrees (positive = right)
        angle_vertical: Vertical rotation in degrees (positive = up)
        target_object: Object name to orbit around (uses object center)
        target_point: [x, y, z] point to orbit around (if no target_object)

    Returns:
        New camera position and angles
    """

    return route_scene_camera_orbit(
        ctx,
        angle_horizontal=angle_horizontal,
        angle_vertical=angle_vertical,
        target_object=target_object,
        target_point=target_point,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        parse_coordinate_fn=parse_coordinate,
    )


def scene_camera_focus(ctx: Context, object_name: str, zoom_factor: float = 1.0) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Focuses viewport camera on object.
    Use `object_name` here, not `target`, `target_object`, or `focus_target`.

    Workflow: AFTER → scene_set_active_object | USE FOR → centering view on component

    Args:
        object_name: Object to focus on. Use `object_name` here; do not use `target`,
            `target_object`, or `focus_target`.
        zoom_factor: 1.0 = fit to view, <1.0 = zoom out, >1.0 = zoom in

    Returns:
        Success message
    """

    return route_scene_camera_focus(
        ctx,
        object_name=object_name,
        zoom_factor=zoom_factor,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


# TASK-045: Object Inspection Tools


def scene_get_custom_properties(ctx: Context, object_name: str) -> SceneCustomPropertiesContract | str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets custom properties (metadata) from an object.

    Workflow: READ-ONLY | USE FOR → understanding object annotations/metadata

    Custom properties are key-value pairs stored on Blender objects.
    They can contain strings, numbers, arrays, or nested data.
    Useful for: object descriptions, export tags, rig parameters, game properties.

    Args:
        object_name: Name of the object to query

    Returns:
        JSON with custom properties including property names, values, and count.
    """

    return route_scene_get_custom_properties(
        ctx,
        object_name=object_name,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_set_custom_property(
    ctx: Context,
    object_name: str,
    property_name: str,
    property_value: Union[str, int, float, bool],
    delete: bool = False,
) -> str:
    """
    [OBJECT MODE][NON-DESTRUCTIVE] Sets or deletes a custom property on an object.

    Workflow: AFTER → scene_get_custom_properties | USE FOR → annotating objects

    Custom properties are preserved through file saves and exports (GLB, FBX).
    Use for: descriptions, comments, export tags, game properties.

    Args:
        object_name: Name of the object to modify
        property_name: Name of the custom property
        property_value: Value to set (string, int, float, or bool)
        delete: If True, removes the property instead of setting it

    Returns:
        Success message with property details
    """

    return route_scene_set_custom_property(
        ctx,
        object_name=object_name,
        property_name=property_name,
        property_value=property_value,
        delete=delete,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
    )


async def scene_get_hierarchy(
    ctx: Context,
    object_name: Optional[str] = None,
    include_transforms: bool = False,
    assistant_summary: bool = False,
) -> SceneHierarchyContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets parent-child hierarchy for objects.

    Workflow: READ-ONLY | USE FOR → understanding object relationships

    If object_name is provided, returns hierarchy for that object (parents + children).
    If object_name is None, returns full scene hierarchy tree.

    Args:
        object_name: Specific object to query (None for full scene)
        include_transforms: Include local/world transform offsets
        assistant_summary: If True, attaches a bounded assistant summary for the hierarchy payload.

    Returns:
        JSON with hierarchy information including parent, children, depth, and path.
    """

    def execute():
        return execute_scene_get_hierarchy(
            ctx=ctx,
            object_name=object_name,
            include_transforms=include_transforms,
            get_scene_handler=get_scene_handler,
            info=ctx_info,
        )

    result = route_tool_call(
        tool_name="scene_get_hierarchy",
        params={
            "object_name": object_name,
            "include_transforms": include_transforms,
            "assistant_summary": assistant_summary,
        },
        direct_executor=execute,
    )
    if not isinstance(result, SceneHierarchyContract):
        return SceneHierarchyContract(error=str(result))
    if not assistant_summary:
        return result
    return await _maybe_attach_scene_state_assistant(
        ctx,
        result,
        subject="scene_get_hierarchy",
        object_name=object_name,
    )


async def scene_get_bounding_box(
    ctx: Context,
    object_name: str,
    world_space: bool = True,
    assistant_summary: bool = False,
) -> SceneBoundingBoxContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets bounding box corners for an object.

    Workflow: READ-ONLY | USE FOR → spatial analysis, collision detection planning

    Returns all 8 corners of the axis-aligned bounding box plus center and dimensions.

    Args:
        object_name: Name of the object to query
        world_space: If True, returns world coordinates. If False, local coordinates.
        assistant_summary: If True, attaches a bounded assistant summary for the bounding-box payload.

    Returns:
        JSON with bounding box data including min, max, center, dimensions, corners, and volume.
    """

    def execute():
        return execute_scene_get_bounding_box(
            ctx=ctx,
            object_name=object_name,
            world_space=world_space,
            get_scene_handler=get_scene_handler,
            info=ctx_info,
        )

    result = route_tool_call(
        tool_name="scene_get_bounding_box",
        params={
            "object_name": object_name,
            "world_space": world_space,
            "assistant_summary": assistant_summary,
        },
        direct_executor=execute,
    )
    if not isinstance(result, SceneBoundingBoxContract):
        return SceneBoundingBoxContract(error=str(result))
    if not assistant_summary:
        return result
    return await _maybe_attach_scene_state_assistant(
        ctx,
        result,
        subject="scene_get_bounding_box",
        object_name=object_name,
    )


async def scene_get_origin_info(
    ctx: Context,
    object_name: str,
    assistant_summary: bool = False,
) -> SceneOriginInfoContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets origin (pivot point) information for an object.

    Workflow: READ-ONLY | USE FOR → transformation planning, origin adjustment decisions

    Returns origin location relative to geometry and bounding box.
    Helps determine if origin should be moved (e.g., to center, to bottom, to cursor).

    Args:
        object_name: Name of the object to query
        assistant_summary: If True, attaches a bounded assistant summary for the origin payload.

    Returns:
        JSON with origin information including world/local position, relative bbox position, and suggestions.
    """

    def execute():
        return execute_scene_get_origin_info(
            ctx=ctx,
            object_name=object_name,
            get_scene_handler=get_scene_handler,
            info=ctx_info,
        )

    result = route_tool_call(
        tool_name="scene_get_origin_info",
        params={"object_name": object_name, "assistant_summary": assistant_summary},
        direct_executor=execute,
    )
    if not isinstance(result, SceneOriginInfoContract):
        return SceneOriginInfoContract(error=str(result))
    if not assistant_summary:
        return result
    return await _maybe_attach_scene_state_assistant(
        ctx,
        result,
        subject="scene_get_origin_info",
        object_name=object_name,
    )


def scene_scope_graph(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
) -> SceneScopeGraphResponseContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Returns the compact structural scope graph for the active guided target set.

    Use this when you need one explicit answer to:
    - what the current scope kind is
    - which object is the structural anchor
    - which objects behave like core masses, appendages, or accessories

    This is a read-only spatial-state artifact. It stays separate from the staged
    reference checkpoint payloads so the guided loop can request it only when the
    current reasoning step genuinely needs richer structural scope detail.

    Args:
        target_object: Optional primary object to force into scope.
        target_objects: Optional additional object names for an explicit object set.
        collection_name: Optional collection to expand into the scope artifact.
    """

    return route_scene_scope_graph(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        guided_scope_requirement_error_fn=_guided_scope_requirement_error,
        should_require_explicit_guided_scope_fn=_should_require_explicit_guided_scope,
        guided_scope_mismatch_message_fn=_guided_scope_mismatch_message,
        record_guided_flow_spatial_check_completion_fn=record_guided_flow_spatial_check_completion,
    )


async def _scene_scope_graph_async(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
) -> SceneScopeGraphResponseContract:
    """Async registered variant that awaits guided spatial-check state updates."""

    return await route_scene_scope_graph_async(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_async_fn=route_tool_call_async,
        hydrate_sync_route_session_fn=_hydrate_sync_route_session,
        guided_scope_requirement_error_fn=_guided_scope_requirement_error,
        should_require_explicit_guided_scope_fn=_should_require_explicit_guided_scope,
        guided_scope_mismatch_message_fn=_guided_scope_mismatch_message,
        get_session_capability_state_async_fn=get_session_capability_state_async,
        record_guided_flow_spatial_check_completion_async_fn=record_guided_flow_spatial_check_completion_async,
        describe_guided_flow_feedback_fn=describe_guided_flow_feedback,
        ctx_info_fn=ctx_info,
    )


def scene_relation_graph(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    goal_hint: str | None = None,
) -> SceneRelationGraphResponseContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Returns the compact spatial relation graph for the active guided target set.

    The graph is derived from current truth primitives such as gap/alignment/overlap/contact checks.
    It exposes typed pair relations and verdicts without forcing the caller to reconstruct them from
    scattered measure/assert calls.

    Args:
        target_object: Optional primary object to force into scope.
        target_objects: Optional additional object names for an explicit object set.
        collection_name: Optional collection to expand into the relation graph scope.
        goal_hint: Optional goal text used only for bounded pair expansion such as symmetry/support candidates.
    """

    return route_scene_relation_graph(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        goal_hint=goal_hint,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        guided_scope_requirement_error_fn=_guided_scope_requirement_error,
        should_require_explicit_guided_scope_fn=_should_require_explicit_guided_scope,
        guided_scope_mismatch_message_fn=_guided_scope_mismatch_message,
        record_guided_flow_spatial_check_completion_fn=record_guided_flow_spatial_check_completion,
        update_quality_gate_plan_from_relation_graph_fn=update_quality_gate_plan_from_relation_graph,
    )


async def _scene_relation_graph_async(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    goal_hint: str | None = None,
) -> SceneRelationGraphResponseContract:
    """Async registered variant that awaits guided spatial-check state updates."""

    return await route_scene_relation_graph_async(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        goal_hint=goal_hint,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_async_fn=route_tool_call_async,
        hydrate_sync_route_session_fn=_hydrate_sync_route_session,
        guided_scope_requirement_error_fn=_guided_scope_requirement_error,
        should_require_explicit_guided_scope_fn=_should_require_explicit_guided_scope,
        guided_scope_mismatch_message_fn=_guided_scope_mismatch_message,
        get_session_capability_state_async_fn=get_session_capability_state_async,
        record_guided_flow_spatial_check_completion_async_fn=record_guided_flow_spatial_check_completion_async,
        update_quality_gate_plan_from_relation_graph_async_fn=update_quality_gate_plan_from_relation_graph_async,
        describe_guided_flow_feedback_fn=describe_guided_flow_feedback,
        ctx_info_fn=ctx_info,
    )


def scene_view_diagnostics(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    camera_name: str | None = None,
    focus_target: str | None = None,
    view_name: Literal["FRONT", "RIGHT", "TOP"] | None = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float | None = None,
    persist_view: bool = False,
) -> SceneViewDiagnosticsResponseContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Returns compact view-space diagnostics for one explicit target scope.

    Use this when you need typed answers to questions like:
    - is the target actually on screen from this camera or viewport?
    - is it fully visible, partially visible, or fully occluded?
    - how centered is it in the current frame?

    This is a view-space artifact only. It reports projection/framing/occlusion facts
    for the current camera or live USER_PERSPECTIVE path; it does not claim contact,
    attachment, overlap, or other truth-space geometry semantics.

    Args:
        target_object: Optional primary object to force into the diagnostics scope.
        target_objects: Optional additional object names for an explicit object set.
        collection_name: Optional collection to expand into the diagnostics scope.
        camera_name: Optional explicit named camera. Use None or "USER_PERSPECTIVE" for the live 3D view.
        focus_target: Optional target to focus before USER_PERSPECTIVE diagnostics.
        view_name: Optional standard USER_PERSPECTIVE preset ('FRONT', 'RIGHT', 'TOP').
        orbit_horizontal: Optional horizontal orbit in degrees for USER_PERSPECTIVE diagnostics.
        orbit_vertical: Optional vertical orbit in degrees for USER_PERSPECTIVE diagnostics.
        zoom_factor: Optional USER_PERSPECTIVE zoom factor.
        persist_view: If True, keeps any USER_PERSPECTIVE adjustment after diagnostics. Defaults to False.
    """

    return route_scene_view_diagnostics(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        camera_name=camera_name,
        focus_target=focus_target,
        view_name=view_name,
        orbit_horizontal=orbit_horizontal,
        orbit_vertical=orbit_vertical,
        zoom_factor=zoom_factor,
        persist_view=persist_view,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        guided_scope_requirement_error_fn=_guided_scope_requirement_error,
        guided_scope_mismatch_message_fn=_guided_scope_mismatch_message,
        view_diagnostics_can_complete_guided_check_fn=_view_diagnostics_can_complete_guided_check,
        record_guided_flow_spatial_check_completion_fn=record_guided_flow_spatial_check_completion,
    )


async def _scene_view_diagnostics_async(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    camera_name: str | None = None,
    focus_target: str | None = None,
    view_name: Literal["FRONT", "RIGHT", "TOP"] | None = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float | None = None,
    persist_view: bool = False,
) -> SceneViewDiagnosticsResponseContract:
    """Async registered variant that awaits guided spatial-check state updates."""

    return await route_scene_view_diagnostics_async(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        camera_name=camera_name,
        focus_target=focus_target,
        view_name=view_name,
        orbit_horizontal=orbit_horizontal,
        orbit_vertical=orbit_vertical,
        zoom_factor=zoom_factor,
        persist_view=persist_view,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_async_fn=route_tool_call_async,
        hydrate_sync_route_session_fn=_hydrate_sync_route_session,
        guided_scope_requirement_error_fn=_guided_scope_requirement_error,
        guided_scope_mismatch_message_fn=_guided_scope_mismatch_message,
        view_diagnostics_can_complete_guided_check_fn=_view_diagnostics_can_complete_guided_check,
        get_session_capability_state_async_fn=get_session_capability_state_async,
        record_guided_flow_spatial_check_completion_async_fn=record_guided_flow_spatial_check_completion_async,
        describe_guided_flow_feedback_fn=describe_guided_flow_feedback,
        ctx_info_fn=ctx_info,
    )


def scene_measure_distance(
    ctx: Context,
    from_object: str,
    to_object: str,
    reference: Literal["ORIGIN", "BBOX_CENTER"] = "ORIGIN",
) -> SceneMeasureDistanceContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Measures distance between two objects.

    Workflow: READ-ONLY | USE FOR → spacing, fit, proportion verification

    Measures either origin-to-origin or bounding-box-center distance.

    Args:
        from_object: Source object name
        to_object: Target object name
        reference: Distance reference mode: ORIGIN or BBOX_CENTER

    Returns:
        Structured distance payload with reference points, axis delta, and units.
    """

    return route_scene_measure_distance(
        ctx,
        from_object=from_object,
        to_object=to_object,
        reference=reference,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_measure_dimensions(
    ctx: Context,
    object_name: str,
    world_space: bool = True,
) -> SceneMeasureDimensionsContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Measures object dimensions from its bounding box.

    Workflow: READ-ONLY | USE FOR → proportions, scaling checks, truth-layer verification

    Args:
        object_name: Object to measure
        world_space: If True, measures transformed world dimensions. If False, measures local dimensions.

    Returns:
        Structured dimensions payload with units and volume estimate.
    """

    return route_scene_measure_dimensions(
        ctx,
        object_name=object_name,
        world_space=world_space,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_measure_gap(
    ctx: Context,
    from_object: str,
    to_object: str,
    tolerance: float = 0.0001,
) -> SceneMeasureGapContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Measures the nearest gap/contact state between two objects.

    Workflow: READ-ONLY | USE FOR → clearance, contact, and fit verification

    Uses the current truth path for the pair. For mesh pairs the handler prefers
    a bounded mesh-surface relation and also reports bbox fallback diagnostics
    such as `bbox_relation`; otherwise it falls back to bbox-only semantics.
    `gap=0` still means the measured relation resolved to either contact or
    overlap, so inspect `relation` plus `measurement_basis` to understand what
    was actually proven.

    Args:
        from_object: Source object name
        to_object: Target object name
        tolerance: Contact threshold in Blender units

    Returns:
        Structured gap payload with relation classification, `measurement_basis`,
        and bbox fallback diagnostics when available.
    """

    return route_scene_measure_gap(
        ctx,
        from_object=from_object,
        to_object=to_object,
        tolerance=tolerance,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_measure_alignment(
    ctx: Context,
    from_object: str,
    to_object: str,
    axes: List[str] | None = None,
    reference: Literal["CENTER", "MIN", "MAX"] = "CENTER",
    tolerance: float = 0.0001,
) -> SceneMeasureAlignmentContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Measures alignment between two objects across chosen axes.

    Workflow: READ-ONLY | USE FOR → centerline, flush-edge, and level checks

    Compares world-space bounding-box `CENTER`, `MIN`, or `MAX` positions on the requested axes.

    Args:
        from_object: Source object name
        to_object: Target object name
        axes: Axes to compare (defaults to X, Y, Z)
        reference: Alignment reference: CENTER, MIN, or MAX
        tolerance: Alignment threshold in Blender units

    Returns:
        Structured alignment payload with per-axis deltas and aligned/misaligned axes.
    """

    return route_scene_measure_alignment(
        ctx,
        from_object=from_object,
        to_object=to_object,
        axes=axes,
        reference=reference,
        tolerance=tolerance,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_measure_overlap(
    ctx: Context,
    from_object: str,
    to_object: str,
    tolerance: float = 0.0001,
) -> SceneMeasureOverlapContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Measures overlap/intersection between two objects.

    Workflow: READ-ONLY | USE FOR → collision, clipping, and fit verification

    Uses the current truth path for the pair. For mesh pairs the handler prefers
    mesh-surface overlap/contact semantics and keeps bbox overlap/touching
    diagnostics alongside them; otherwise it falls back to bbox-only
    classification.

    Args:
        from_object: Source object name
        to_object: Target object name
        tolerance: Touch/intersection threshold in Blender units

    Returns:
        Structured overlap payload with `measurement_basis`, current relation,
        and bbox fallback diagnostics when available.
    """

    return route_scene_measure_overlap(
        ctx,
        from_object=from_object,
        to_object=to_object,
        tolerance=tolerance,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_assert_contact(
    ctx: Context,
    from_object: str,
    to_object: str,
    max_gap: float = 0.0001,
    allow_overlap: bool = False,
) -> SceneAssertContactContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Asserts that two objects satisfy the expected contact relation.

    Workflow: READ-ONLY | USE FOR → deterministic fit/contact postconditions

    Objects pass when the measured gap from the current truth path is within
    `max_gap`, and overlap is rejected unless `allow_overlap=True`. For mesh
    pairs this now prefers mesh-surface contact semantics instead of bbox
    touching alone, while still exposing bbox fallback diagnostics in the
    assertion details.

    Args:
        from_object: Source object name
        to_object: Target object name
        max_gap: Maximum allowed separation in Blender units
        allow_overlap: If True, overlap is accepted as a passing relation

    Returns:
        Structured assertion payload with pass/fail result, current measured
        relation, and `measurement_basis` / bbox diagnostics in `details`.
    """

    return route_scene_assert_contact(
        ctx,
        from_object=from_object,
        to_object=to_object,
        max_gap=max_gap,
        allow_overlap=allow_overlap,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_assert_dimensions(
    ctx: Context,
    object_name: str,
    expected_dimensions: Union[str, List[float]],
    tolerance: float = 0.0001,
    world_space: bool = True,
) -> SceneAssertDimensionsContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Asserts that object dimensions match an expected vector.

    Workflow: READ-ONLY | USE FOR → explicit size verification without outer-LLM arithmetic

    Args:
        object_name: Object to verify
        expected_dimensions: Expected [x, y, z] dimensions as a list or string
        tolerance: Allowed per-axis difference in Blender units
        world_space: If True, compares world dimensions. If False, compares local dimensions.

    Returns:
        Structured assertion payload with expected dimensions, actual dimensions, and per-axis delta.
    """

    return route_scene_assert_dimensions(
        ctx,
        object_name=object_name,
        expected_dimensions=expected_dimensions,
        tolerance=tolerance,
        world_space=world_space,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
        parse_coordinate_fn=parse_coordinate,
    )


def scene_assert_containment(
    ctx: Context,
    inner_object: str,
    outer_object: str,
    min_clearance: float = 0.0,
    tolerance: float = 0.0001,
) -> SceneAssertContainmentContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Asserts that one object is contained inside another.

    Workflow: READ-ONLY | USE FOR → inset, fit, enclosure, and clearance postconditions

    Args:
        inner_object: Object that should remain inside
        outer_object: Container object
        min_clearance: Required minimum clearance to the container bounds
        tolerance: Allowed comparison tolerance in Blender units

    Returns:
        Structured assertion payload with containment pass/fail result and measured clearance/protrusion details.
    """

    return route_scene_assert_containment(
        ctx,
        inner_object=inner_object,
        outer_object=outer_object,
        min_clearance=min_clearance,
        tolerance=tolerance,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_assert_symmetry(
    ctx: Context,
    left_object: str,
    right_object: str,
    axis: Literal["X", "Y", "Z"] = "X",
    mirror_coordinate: float = 0.0,
    tolerance: float = 0.0001,
) -> SceneAssertSymmetryContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Asserts symmetry between two objects across a mirror plane.

    Workflow: READ-ONLY | USE FOR → mirrored-part verification and bilateral layout checks

    Args:
        left_object: First object in the pair
        right_object: Second object in the pair
        axis: Mirror axis
        mirror_coordinate: Coordinate of the mirror plane on that axis
        tolerance: Allowed comparison tolerance in Blender units

    Returns:
        Structured assertion payload with center/dimension deltas and pass/fail symmetry result.
    """

    return route_scene_assert_symmetry(
        ctx,
        left_object=left_object,
        right_object=right_object,
        axis=axis,
        mirror_coordinate=mirror_coordinate,
        tolerance=tolerance,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )


def scene_assert_proportion(
    ctx: Context,
    object_name: str,
    axis_a: Literal["X", "Y", "Z"],
    expected_ratio: float,
    axis_b: Literal["X", "Y", "Z"] | None = None,
    reference_object: str | None = None,
    reference_axis: Literal["X", "Y", "Z"] | None = None,
    tolerance: float = 0.01,
    world_space: bool = True,
) -> SceneAssertProportionContract:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Asserts a proportion/ratio against the expected value.

    Workflow: READ-ONLY | USE FOR → proportion postconditions without outer-LLM arithmetic

    Args:
        object_name: Primary object for the numerator axis
        axis_a: Numerator axis on the primary object
        expected_ratio: Expected ratio value
        axis_b: Optional denominator axis on the same object
        reference_object: Optional denominator object for cross-object ratios
        reference_axis: Optional denominator axis on the reference object
        tolerance: Allowed ratio delta
        world_space: If True, uses world dimensions. If False, uses local dimensions.

    Returns:
        Structured assertion payload with expected ratio, actual ratio, and pass/fail result.
    """

    return route_scene_assert_proportion(
        ctx,
        object_name=object_name,
        axis_a=axis_a,
        expected_ratio=expected_ratio,
        axis_b=axis_b,
        reference_object=reference_object,
        reference_axis=reference_axis,
        tolerance=tolerance,
        world_space=world_space,
        get_scene_handler_fn=get_scene_handler,
        route_tool_call_fn=route_tool_call,
        ctx_info_fn=ctx_info,
    )
