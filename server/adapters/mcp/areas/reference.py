# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Goal-scoped reference image intake and lifecycle tools."""

from __future__ import annotations

import base64
import mimetypes
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.reference import (
    ReferenceCompareCheckpointResponseContract,
    ReferenceCompareStageCheckpointResponseContract,
    ReferenceImagesResponseContract,
    ReferenceIterateStageCheckpointResponseContract,
)
from server.adapters.mcp.sampling.result_types import to_vision_assistant_contract
from server.adapters.mcp.session_capabilities import (
    get_session_capability_state_async,
    replace_session_pending_reference_images_async,
    replace_session_reference_images_async,
)
from server.adapters.mcp.session_state import get_session_value_async, set_session_value_async
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.adapters.mcp.vision import (
    CapturePresetProfile,
    VisionImageInput,
    VisionRequest,
    build_reference_capture_images,
    build_vision_request_from_stage_captures,
    capture_stage_images,
    run_vision_assist,
    select_reference_records_for_target,
)
from server.infrastructure.di import get_collection_handler, get_scene_handler, get_vision_backend_resolver
from server.infrastructure.tmp_paths import get_reference_image_storage_path, get_viewport_output_paths

REFERENCE_PUBLIC_TOOL_NAMES = (
    "reference_images",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
)
_ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
_REFERENCE_CORRECTION_LOOP_STATE_KEY = "reference_correction_loop"
_REFERENCE_CORRECTION_STAGNATION_THRESHOLD = 2


def _register_existing_tool(target, tool_name: str):
    tool = globals()[tool_name]
    fn = getattr(tool, "fn", tool)
    return target.tool(fn, name=tool_name, tags=set(get_capability_tags("reference")))


def register_reference_tools(target):
    return {tool_name: _register_existing_tool(target, tool_name) for tool_name in REFERENCE_PUBLIC_TOOL_NAMES}


def _sorted_references(references: list[dict]) -> list[dict]:
    return sorted(references, key=lambda item: str(item.get("added_at") or ""))


def _as_response(
    *,
    action: str,
    goal: str | None,
    references: list[dict],
    removed_reference_id: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceImagesResponseContract:
    return ReferenceImagesResponseContract(
        action=action,
        goal=goal,
        reference_count=len(references),
        references=references,
        removed_reference_id=removed_reference_id,
        message=message,
        error=error,
    )


def _validate_local_reference_path(source_path: str) -> Path:
    path = Path(source_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"Reference image path does not exist: {source_path}")
    if path.suffix.lower() not in _ALLOWED_IMAGE_SUFFIXES:
        raise ValueError("Reference image must be one of: .png, .jpg, .jpeg, .webp")
    return path


def _copy_reference_image(source_path: Path) -> tuple[str, str]:
    filename = f"ref_{uuid4().hex[:10]}{source_path.suffix.lower()}"
    internal_path, host_visible_path = get_reference_image_storage_path(filename)
    shutil.copy2(source_path, internal_path)
    return str(internal_path), host_visible_path


def _compare_response(
    *,
    action: str,
    checkpoint_path: str,
    checkpoint_label: str | None,
    goal: str | None,
    target_object: str | None,
    target_view: str | None,
    reference_ids: list[str],
    reference_labels: list[str],
    vision_assistant=None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareCheckpointResponseContract:
    return ReferenceCompareCheckpointResponseContract(
        action=action,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        checkpoint_path=checkpoint_path,
        checkpoint_label=checkpoint_label,
        reference_count=len(reference_ids),
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


def _stage_compare_response(
    *,
    checkpoint_id: str,
    checkpoint_label: str | None,
    goal: str | None,
    target_object: str | None,
    target_objects: list[str],
    collection_name: str | None,
    target_view: str | None,
    preset_profile: CapturePresetProfile,
    preset_names: list[str],
    captures: list | tuple = (),
    reference_ids: list[str],
    reference_labels: list[str],
    vision_assistant=None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareStageCheckpointResponseContract:
    return ReferenceCompareStageCheckpointResponseContract(
        action="compare_stage_checkpoint",
        goal=goal,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        target_view=target_view,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        preset_profile=preset_profile,
        preset_names=preset_names,
        capture_count=len(captures),
        captures=list(captures),
        reference_count=len(reference_ids),
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


def _iterate_stage_response(
    *,
    goal: str | None,
    target_object: str | None,
    target_objects: list[str],
    collection_name: str | None,
    target_view: str | None,
    checkpoint_id: str,
    checkpoint_label: str | None,
    iteration_index: int,
    loop_disposition: str,
    continue_recommended: bool,
    prior_checkpoint_id: str | None,
    prior_correction_focus: list[str],
    correction_focus: list[str],
    repeated_correction_focus: list[str],
    stagnation_count: int,
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    stop_reason: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceIterateStageCheckpointResponseContract:
    return ReferenceIterateStageCheckpointResponseContract(
        action="iterate_stage_checkpoint",
        goal=goal,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        target_view=target_view,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        iteration_index=iteration_index,
        loop_disposition=loop_disposition,
        continue_recommended=continue_recommended,
        prior_checkpoint_id=prior_checkpoint_id,
        prior_correction_focus=prior_correction_focus,
        correction_focus=correction_focus,
        repeated_correction_focus=repeated_correction_focus,
        stagnation_count=stagnation_count,
        stop_reason=stop_reason,
        compare_result=compare_result,
        message=message,
        error=error,
    )


def _normalized_focus_key(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _resolve_actionable_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    vision_result = compare_result.vision_assistant.result if compare_result.vision_assistant else None
    if vision_result is None:
        return []

    ordered = list(vision_result.correction_focus or [])
    if not ordered:
        ordered.extend(vision_result.shape_mismatches or [])
        ordered.extend(vision_result.proportion_mismatches or [])
        ordered.extend(vision_result.next_corrections or [])

    deduped: list[str] = []
    seen: set[str] = set()
    for item in ordered:
        normalized = _normalized_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def _dedupe_names(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        normalized = item.strip()
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _resolve_capture_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> tuple[str | None, list[str], str | None]:
    resolved_target_objects = _dedupe_names(list(target_objects or []))
    if target_object:
        resolved_target_objects = _dedupe_names([target_object, *resolved_target_objects])

    if collection_name:
        collection_payload = get_collection_handler().list_objects(
            collection_name=collection_name,
            recursive=True,
            include_hidden=False,
        )
        collection_objects = [
            str(item.get("name")).strip()
            for item in collection_payload.get("objects", [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]
        resolved_target_objects = _dedupe_names([*resolved_target_objects, *collection_objects])

    normalized_primary = target_object if target_object else (resolved_target_objects[0] if len(resolved_target_objects) == 1 else None)
    return normalized_primary, resolved_target_objects, collection_name


def _repeated_focus(current: list[str], prior: list[str]) -> list[str]:
    prior_keys = {_normalized_focus_key(item) for item in prior if _normalized_focus_key(item)}
    repeated: list[str] = []
    for item in current:
        normalized = _normalized_focus_key(item)
        if normalized and normalized in prior_keys:
            repeated.append(item)
    return repeated


async def _run_checkpoint_compare(
    ctx: Context,
    *,
    checkpoint: Path,
    checkpoint_label: str | None,
    target_object: str | None,
    target_view: str | None,
    goal_override: str | None,
    prompt_hint: str | None,
    response_action: str,
) -> ReferenceCompareCheckpointResponseContract:
    """Shared bounded checkpoint compare path."""

    session = await get_session_capability_state_async(ctx)
    goal = goal_override or session.goal
    if not goal:
        return _compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing a checkpoint, or pass goal_override.",
        )

    references = list(session.reference_images or [])
    selected_reference_records = select_reference_records_for_target(
        references,
        target_object=target_object,
        target_view=target_view,
    )
    if not selected_reference_records:
        return _compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="No matching reference images are attached for the requested target_object/target_view.",
        )

    reference_images = build_reference_capture_images(selected_reference_records)
    vision_request = VisionRequest(
        goal=goal,
        images=(
            VisionImageInput(
                path=str(checkpoint),
                role="after",
                label=checkpoint_label or checkpoint.name,
                media_type=mimetypes.guess_type(str(checkpoint))[0] or "image/png",
            ),
            *tuple(
                VisionImageInput(
                    path=item.image_path,
                    role="reference",
                    label=item.label,
                    media_type=item.media_type,
                )
                for item in reference_images
            ),
        ),
        target_object=target_object,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=checkpoint_vs_reference",
                f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                f"target_view={target_view}" if target_view else None,
                *[
                    f"reference[{index}] label={record.label}"
                    for index, record in enumerate(selected_reference_records, start=1)
                    if record.label
                ],
            )
            if part
        )
        or None,
        metadata={
            "source": response_action,
            "checkpoint_path": str(checkpoint),
            "reference_count": len(selected_reference_records),
        },
    )
    outcome = await run_vision_assist(
        ctx,
        request=vision_request,
        resolver=get_vision_backend_resolver(),
    )
    vision_assistant = to_vision_assistant_contract(outcome)
    return _compare_response(
        action=response_action,
        checkpoint_path=str(checkpoint),
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        vision_assistant=vision_assistant,
        message=(
            f"Compared checkpoint '{checkpoint_label or checkpoint.name}' against {len(selected_reference_records)} reference image(s)."
            if outcome.status == "success"
            else "Checkpoint comparison executed but vision assistance did not complete successfully."
        ),
        error=vision_assistant.rejection_reason if vision_assistant.status != "success" else None,
    )


async def _run_stage_checkpoint_compare(
    ctx: Context,
    *,
    checkpoint_id: str,
    checkpoint_label: str | None,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
    target_view: str | None,
    preset_profile: CapturePresetProfile,
    goal_override: str | None,
    prompt_hint: str | None,
) -> ReferenceCompareStageCheckpointResponseContract:
    """Capture one deterministic stage view-set, then compare it against references."""

    session = await get_session_capability_state_async(ctx)
    goal = goal_override or session.goal
    if not goal:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing a stage checkpoint, or pass goal_override.",
        )

    try:
        resolved_target_object, resolved_target_objects, resolved_collection_name = _resolve_capture_scope(
            target_object=target_object,
            target_objects=target_objects,
            collection_name=collection_name,
        )
    except RuntimeError as exc:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )

    references = list(session.reference_images or [])
    selected_reference_records = select_reference_records_for_target(
        references,
        target_object=resolved_target_object,
        target_view=target_view,
    )
    if not selected_reference_records:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            error="No matching reference images are attached for the requested target_object/target_view.",
        )

    try:
        captures = capture_stage_images(
            get_scene_handler(),
            bundle_id=checkpoint_id,
            stage="after",
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            preset_profile=preset_profile,
        )
    except RuntimeError as exc:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[item.reference_id for item in selected_reference_records],
            reference_labels=[item.label or item.reference_id for item in selected_reference_records],
            error=str(exc),
        )

    reference_images = build_reference_capture_images(selected_reference_records)
    vision_request = build_vision_request_from_stage_captures(
        captures,
        goal=goal,
        target_object=resolved_target_object,
        reference_images=reference_images,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=stage_checkpoint_vs_reference",
                f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                f"preset_profile={preset_profile}",
                f"collection_name={resolved_collection_name}" if resolved_collection_name else None,
                f"target_objects={','.join(resolved_target_objects)}" if resolved_target_objects else None,
                f"target_view={target_view}" if target_view else None,
                *[
                    f"capture[{index}] label={capture.label}"
                    for index, capture in enumerate(captures, start=1)
                ],
                *[
                    f"reference[{index}] label={record.label}"
                    for index, record in enumerate(selected_reference_records, start=1)
                    if record.label
                ],
            )
            if part
        )
        or None,
        metadata={
            "source": "compare_stage_checkpoint",
            "checkpoint_id": checkpoint_id,
            "preset_profile": preset_profile,
            "capture_count": len(captures),
            "collection_name": resolved_collection_name,
            "target_objects": list(resolved_target_objects),
        },
    )
    outcome = await run_vision_assist(
        ctx,
        request=vision_request,
        resolver=get_vision_backend_resolver(),
    )
    vision_assistant = to_vision_assistant_contract(outcome)
    return _stage_compare_response(
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=resolved_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
        target_view=target_view,
        preset_profile=preset_profile,
        preset_names=[capture.preset_name or capture.label for capture in captures],
        captures=captures,
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        vision_assistant=vision_assistant,
        message=(
            f"Captured and compared stage checkpoint '{checkpoint_label or checkpoint_id}' using {len(captures)} deterministic view(s)."
            if outcome.status == "success"
            else "Stage checkpoint capture executed but vision assistance did not complete successfully."
        ),
        error=vision_assistant.rejection_reason if vision_assistant.status != "success" else None,
    )


async def reference_images(
    ctx: Context,
    action: str,
    source_path: str | None = None,
    reference_id: str | None = None,
    label: str | None = None,
    notes: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
) -> ReferenceImagesResponseContract:
    """Manage goal-scoped reference images for later vision/capture interpretation."""

    normalized_action = str(action).lower()
    if normalized_action not in {"attach", "list", "remove", "clear"}:
        return _as_response(action="list", goal=None, references=[], error="action must be attach, list, remove, or clear")

    session = await get_session_capability_state_async(ctx)
    active_references = list(session.reference_images or [])
    pending_references = list(session.pending_reference_images or [])
    references = active_references if session.goal is not None else pending_references

    if normalized_action == "list":
        return _as_response(action="list", goal=session.goal, references=_sorted_references(references))

    if normalized_action == "clear":
        for item in references:
            stored_path = item.get("stored_path")
            if isinstance(stored_path, str):
                try:
                    Path(stored_path).unlink(missing_ok=True)
                except Exception:
                    pass
        if session.goal is None:
            await replace_session_pending_reference_images_async(ctx, [])
            ctx_info(ctx, "[REFERENCE] Cleared pending reference images")
            return _as_response(action="clear", goal=None, references=[], message="Cleared pending reference images.")

        await replace_session_reference_images_async(ctx, [])
        ctx_info(ctx, "[REFERENCE] Cleared session reference images")
        return _as_response(action="clear", goal=session.goal, references=[], message="Cleared session reference images.")

    if normalized_action == "remove":
        if not reference_id:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(references),
                error="reference_id is required for remove",
            )
        remaining: list[dict] = []
        removed: dict | None = None
        for item in references:
            if item.get("reference_id") == reference_id and removed is None:
                removed = item
                continue
            remaining.append(item)
        if removed is None:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(references),
                error=f"Reference image not found: {reference_id}",
            )
        stored_path = removed.get("stored_path")
        if isinstance(stored_path, str):
            try:
                Path(stored_path).unlink(missing_ok=True)
            except Exception:
                pass
        if session.goal is None:
            await replace_session_pending_reference_images_async(ctx, remaining)
        else:
            await replace_session_reference_images_async(ctx, remaining)
        ctx_info(ctx, f"[REFERENCE] Removed reference image {reference_id}")
        return _as_response(
            action="remove",
            goal=session.goal,
            references=_sorted_references(remaining),
            removed_reference_id=reference_id,
            message=f"Removed reference image '{reference_id}'.",
        )

    if not source_path:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(references),
            error="source_path is required for attach",
        )

    try:
        source = _validate_local_reference_path(source_path)
        stored_path, host_visible_path = _copy_reference_image(source)
    except ValueError as exc:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(references),
            error=str(exc),
        )

    reference = {
        "reference_id": f"ref_{uuid4().hex[:8]}",
        "goal": session.goal or "__pending_goal__",
        "label": label,
        "notes": notes,
        "target_object": target_object,
        "target_view": target_view,
        "media_type": mimetypes.guess_type(str(source))[0] or "image/png",
        "source_kind": "local_path",
        "original_path": str(source),
        "stored_path": stored_path,
        "host_visible_path": host_visible_path,
        "added_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    updated = [*references, reference]
    if session.goal is None:
        await replace_session_pending_reference_images_async(ctx, updated)
        ctx_info(ctx, f"[REFERENCE] Attached pending reference image {reference['reference_id']}")
        return _as_response(
            action="attach",
            goal=None,
            references=_sorted_references(updated),
            message=(
                f"Attached pending reference image '{reference['reference_id']}'. "
                "It will be adopted automatically when the next active goal is set."
            ),
        )

    await replace_session_reference_images_async(ctx, updated)
    ctx_info(ctx, f"[REFERENCE] Attached reference image {reference['reference_id']} for goal '{session.goal}'")
    return _as_response(
        action="attach",
        goal=session.goal,
        references=_sorted_references(updated),
        message=f"Attached reference image '{reference['reference_id']}'.",
    )


async def reference_compare_checkpoint(
    ctx: Context,
    checkpoint_path: str,
    checkpoint_label: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
) -> ReferenceCompareCheckpointResponseContract:
    """Compare one current checkpoint image against the active goal and attached references."""

    try:
        checkpoint = _validate_local_reference_path(checkpoint_path)
    except ValueError as exc:
        return _compare_response(
            action="compare_checkpoint",
            checkpoint_path=checkpoint_path,
            checkpoint_label=checkpoint_label,
            goal=goal_override,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )

    return await _run_checkpoint_compare(
        ctx,
        checkpoint=checkpoint,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        response_action="compare_checkpoint",
    )


async def reference_compare_current_view(
    ctx: Context,
    checkpoint_label: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    width: int = 1280,
    height: int = 960,
    shading: str = "SOLID",
    camera_name: str | None = None,
    focus_target: str | None = None,
    view_name: str | None = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float | None = None,
    persist_view: bool = False,
) -> ReferenceCompareCheckpointResponseContract:
    """Capture one current viewport/camera checkpoint and compare it against attached references."""

    try:
        b64_data = get_scene_handler().get_viewport(
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
        )
    except RuntimeError as exc:
        return _compare_response(
            action="compare_current_view",
            checkpoint_path="",
            checkpoint_label=checkpoint_label,
            goal=goal_override,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"checkpoint_compare_{timestamp}.jpg"
    latest_name = "checkpoint_compare_latest.jpg"
    internal_file, internal_latest, _external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    image_bytes = base64.b64decode(b64_data)
    internal_file.write_bytes(image_bytes)
    internal_latest.write_bytes(image_bytes)

    return await _run_checkpoint_compare(
        ctx,
        checkpoint=internal_file,
        checkpoint_label=checkpoint_label,
        target_object=target_object or focus_target,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=current_view_checkpoint",
                f"camera_name={camera_name}" if camera_name else None,
                f"view_name={view_name}" if view_name else None,
                f"shading={shading}",
            )
            if part
        )
        or None,
        response_action="compare_current_view",
    )


async def reference_compare_stage_checkpoint(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    checkpoint_label: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    preset_profile: CapturePresetProfile = "compact",
) -> ReferenceCompareStageCheckpointResponseContract:
    """Capture one deterministic stage view-set and compare it against attached references."""

    checkpoint_target = collection_name or target_object or "scene"
    checkpoint_id = f"stage_checkpoint_{checkpoint_target}_{uuid4().hex[:8]}"
    return await _run_stage_checkpoint_compare(
        ctx,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        target_view=target_view,
        preset_profile=preset_profile,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
    )


async def reference_iterate_stage_checkpoint(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    checkpoint_label: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    preset_profile: CapturePresetProfile = "compact",
) -> ReferenceIterateStageCheckpointResponseContract:
    """Run one session-aware stage checkpoint iteration and return continuation guidance."""

    compare_result = await reference_compare_stage_checkpoint(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        checkpoint_label=checkpoint_label,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        preset_profile=preset_profile,
    )
    goal = compare_result.goal
    correction_focus = _resolve_actionable_focus(compare_result)
    continue_recommended = bool(correction_focus)
    loop_disposition = "continue_build" if continue_recommended else "stop"
    stop_reason = None if continue_recommended else "No actionable correction guidance was returned for this checkpoint."

    if compare_result.error or goal is None:
        return _iterate_stage_response(
            goal=goal,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            checkpoint_id=compare_result.checkpoint_id,
            checkpoint_label=checkpoint_label,
            iteration_index=1,
            loop_disposition="stop",
            continue_recommended=False,
            prior_checkpoint_id=None,
            prior_correction_focus=[],
            correction_focus=correction_focus,
            repeated_correction_focus=[],
            stagnation_count=0,
            compare_result=compare_result,
            stop_reason=compare_result.error or stop_reason,
            message="Stage iteration did not complete successfully.",
            error=compare_result.error,
        )

    prior_state = await get_session_value_async(ctx, _REFERENCE_CORRECTION_LOOP_STATE_KEY, None)
    if not isinstance(prior_state, dict):
        prior_state = None

    same_loop = (
        prior_state is not None
        and prior_state.get("goal") == goal
        and prior_state.get("target_object") == target_object
        and list(prior_state.get("target_objects") or []) == list(compare_result.target_objects or [])
        and prior_state.get("collection_name") == collection_name
    )
    prior_checkpoint_id = str(prior_state.get("last_checkpoint_id")) if same_loop and prior_state.get("last_checkpoint_id") else None
    prior_correction_focus = list(prior_state.get("last_correction_focus") or []) if same_loop else []
    iteration_index = int(prior_state.get("iteration_index") or 0) + 1 if same_loop else 1
    repeated_correction_focus = _repeated_focus(correction_focus, prior_correction_focus)
    prior_stagnation_count = int(prior_state.get("stagnation_count") or 0) if same_loop else 0
    stagnation_count = prior_stagnation_count + 1 if repeated_correction_focus and correction_focus else 0

    if continue_recommended and stagnation_count >= _REFERENCE_CORRECTION_STAGNATION_THRESHOLD:
        loop_disposition = "inspect_validate"

    await set_session_value_async(
        ctx,
        _REFERENCE_CORRECTION_LOOP_STATE_KEY,
        {
            "goal": goal,
            "target_object": target_object,
            "target_objects": list(compare_result.target_objects or []),
            "collection_name": collection_name,
            "last_checkpoint_id": compare_result.checkpoint_id,
            "last_checkpoint_label": checkpoint_label,
            "last_correction_focus": correction_focus,
            "iteration_index": iteration_index,
            "stagnation_count": stagnation_count,
        },
    )

    if loop_disposition == "inspect_validate":
        message = (
            "Repeated correction focus persists across stage iterations. "
            "Prefer inspect/measure/assert confirmation before another free-form build step."
        )
    elif continue_recommended:
        message = "Continue the guided build loop using correction_focus first."
    else:
        message = "No further correction loop action is recommended for this checkpoint."

    return _iterate_stage_response(
        goal=goal,
        target_object=target_object,
        target_objects=list(compare_result.target_objects or []),
        collection_name=collection_name,
        target_view=target_view,
        checkpoint_id=compare_result.checkpoint_id,
        checkpoint_label=checkpoint_label,
        iteration_index=iteration_index,
        loop_disposition=loop_disposition,
        continue_recommended=continue_recommended,
        prior_checkpoint_id=prior_checkpoint_id,
        prior_correction_focus=prior_correction_focus,
        correction_focus=correction_focus,
        repeated_correction_focus=repeated_correction_focus,
        stagnation_count=stagnation_count,
        compare_result=compare_result,
        stop_reason=stop_reason,
        message=message,
    )
