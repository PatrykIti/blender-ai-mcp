# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Current-view compare helpers for the reference MCP surface."""

from __future__ import annotations

import base64
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from fastmcp import Context

from server.adapters.mcp.contracts.reference import (
    ReferenceCompareCheckpointResponseContract,
    ReferenceViewDiagnosticsHintContract,
)


def _current_view_prompt_hint(
    *,
    prompt_hint: str | None,
    camera_name: str | None,
    view_name: str | None,
    shading: str,
) -> str | None:
    return (
        " | ".join(
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
        or None
    )


def _current_view_diagnostics_kwargs(
    *,
    camera_name: str | None,
    focus_target: str | None,
    view_name: str | None,
    orbit_horizontal: float,
    orbit_vertical: float,
    zoom_factor: float | None,
    persist_view: bool,
) -> dict[str, Any]:
    use_explicit_scene_camera = bool(camera_name and camera_name != "USER_PERSPECTIVE")
    diagnostics_focus_target = focus_target
    diagnostics_view_name = view_name
    diagnostics_orbit_horizontal = orbit_horizontal
    diagnostics_orbit_vertical = orbit_vertical
    diagnostics_zoom_factor = zoom_factor
    if persist_view and not use_explicit_scene_camera:
        diagnostics_focus_target = None
        diagnostics_view_name = None
        diagnostics_orbit_horizontal = 0.0
        diagnostics_orbit_vertical = 0.0
        diagnostics_zoom_factor = None
    return {
        "camera_name": camera_name,
        "focus_target": diagnostics_focus_target,
        "view_name": diagnostics_view_name,
        "orbit_horizontal": diagnostics_orbit_horizontal,
        "orbit_vertical": diagnostics_orbit_vertical,
        "zoom_factor": diagnostics_zoom_factor,
        "persist_view": persist_view,
    }


def _capture_current_view_checkpoint(
    *,
    image_b64: str,
    checkpoint_prefix: str,
    latest_name: str,
    get_viewport_output_paths: Callable[..., tuple[Path, Path, str, str]],
    now: Callable[[], Any],
    new_uuid: Callable[[], Any],
) -> Path:
    timestamp = now().strftime("%Y%m%d_%H%M%S")
    filename = f"{checkpoint_prefix}_{timestamp}_{new_uuid().hex[:8]}.jpg"
    internal_file, internal_latest, _external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    image_bytes = base64.b64decode(image_b64)
    internal_file.write_bytes(image_bytes)
    internal_latest.write_bytes(image_bytes)
    return internal_file


async def run_current_view_compare(
    ctx: Context,
    *,
    checkpoint_label: str | None,
    target_object: str | None,
    target_view: str | None,
    goal_override: str | None,
    prompt_hint: str | None,
    width: int,
    height: int,
    shading: str,
    camera_name: str | None,
    focus_target: str | None,
    view_name: str | None,
    orbit_horizontal: float,
    orbit_vertical: float,
    zoom_factor: float | None,
    persist_view: bool,
    build_compare_response: Callable[..., ReferenceCompareCheckpointResponseContract],
    get_session_capability_state_async: Callable[[Context], Awaitable[Any]],
    get_scene_handler: Callable[[], Any],
    get_viewport_output_paths: Callable[..., tuple[Path, Path, str, str]],
    build_view_diagnostics_hints: Callable[..., list[ReferenceViewDiagnosticsHintContract]],
    run_checkpoint_compare: Callable[..., Awaitable[ReferenceCompareCheckpointResponseContract]],
    now: Callable[[], Any],
    new_uuid: Callable[[], Any],
) -> ReferenceCompareCheckpointResponseContract:
    """Capture one current viewport/camera checkpoint, then compare it to references."""

    session = await get_session_capability_state_async(ctx)
    effective_goal = goal_override or session.goal
    if not effective_goal:
        return build_compare_response(
            action="compare_current_view",
            checkpoint_path="",
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing the current view, or pass goal_override.",
        )

    scene_handler = get_scene_handler()
    try:
        viewport_b64 = scene_handler.get_viewport(
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
        return build_compare_response(
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

    checkpoint = _capture_current_view_checkpoint(
        image_b64=viewport_b64,
        checkpoint_prefix="checkpoint_compare",
        latest_name="checkpoint_compare_latest.jpg",
        get_viewport_output_paths=get_viewport_output_paths,
        now=now,
        new_uuid=new_uuid,
    )

    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None
    diagnostic_target = target_object or focus_target
    if diagnostic_target:
        diagnostics_kwargs = _current_view_diagnostics_kwargs(
            camera_name=camera_name,
            focus_target=focus_target,
            view_name=view_name,
            orbit_horizontal=orbit_horizontal,
            orbit_vertical=orbit_vertical,
            zoom_factor=zoom_factor,
            persist_view=persist_view,
        )
        try:
            diagnostics_payload = scene_handler.get_view_diagnostics(
                target_object=diagnostic_target,
                **diagnostics_kwargs,
            )
            candidate_hints = build_view_diagnostics_hints(
                diagnostics_payload=diagnostics_payload,
                target_object=diagnostic_target,
                camera_name=camera_name,
                focus_target=diagnostics_kwargs["focus_target"],
                view_name=diagnostics_kwargs["view_name"],
                orbit_horizontal=diagnostics_kwargs["orbit_horizontal"],
                orbit_vertical=diagnostics_kwargs["orbit_vertical"],
                zoom_factor=diagnostics_kwargs["zoom_factor"],
            )
            if candidate_hints:
                view_diagnostics_hints = candidate_hints
        except Exception:
            view_diagnostics_hints = None

    compare_result = await run_checkpoint_compare(
        ctx,
        checkpoint=checkpoint,
        checkpoint_label=checkpoint_label,
        target_object=target_object or focus_target,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=_current_view_prompt_hint(
            prompt_hint=prompt_hint,
            camera_name=camera_name,
            view_name=view_name,
            shading=shading,
        ),
        response_action="compare_current_view",
    )
    if view_diagnostics_hints:
        compare_result.view_diagnostics_hints = view_diagnostics_hints
    return compare_result
