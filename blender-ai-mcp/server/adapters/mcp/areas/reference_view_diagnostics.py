# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Advisory view-diagnostics helpers for the reference MCP surface."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.areas.reference_silhouette import select_silhouette_analysis_capture
from server.adapters.mcp.contracts.reference import ReferenceViewDiagnosticsHintContract
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.vision import CapturePresetProfile, CapturePresetSpec, resolve_capture_preset_specs


def _resolve_stage_view_diagnostics_preset(
    *,
    captures: list[VisionCaptureImageContract] | tuple[VisionCaptureImageContract, ...],
    preset_profile: CapturePresetProfile,
    target_view: str | None,
) -> tuple[VisionCaptureImageContract, CapturePresetSpec | None]:
    capture = select_silhouette_analysis_capture(captures=captures, target_view=target_view)
    preset_name = str(capture.preset_name or "").strip()
    if not preset_name:
        return capture, None

    for preset in resolve_capture_preset_specs(preset_profile):
        if preset.name == preset_name:
            return capture, preset
    return capture, None


def build_stage_view_diagnostics_hints(
    *,
    scene_handler: Any,
    captures: list[VisionCaptureImageContract] | tuple[VisionCaptureImageContract, ...],
    preset_profile: CapturePresetProfile,
    target_object: str | None,
    target_objects: list[str] | tuple[str, ...],
    collection_name: str | None,
    target_view: str | None,
) -> list[ReferenceViewDiagnosticsHintContract] | None:
    diagnostic_target = target_object or next((name for name in target_objects if str(name or "").strip()), None)
    if not diagnostic_target or not captures or not hasattr(scene_handler, "get_view_diagnostics"):
        return None

    capture, preset = _resolve_stage_view_diagnostics_preset(
        captures=captures,
        preset_profile=preset_profile,
        target_view=target_view,
    )
    focus_target = (
        diagnostic_target if (preset.focus_target if preset is not None else capture.view_kind == "focus") else None
    )
    view_name = preset.standard_view if preset is not None else None
    orbit_horizontal = float(preset.orbit_horizontal or 0.0) if preset is not None else 0.0
    orbit_vertical = float(preset.orbit_vertical or 0.0) if preset is not None else 0.0
    zoom_factor = None
    if preset is not None and preset.focus_zoom_factor != 1.0:
        zoom_factor = float(preset.focus_zoom_factor)

    try:
        diagnostics_payload = scene_handler.get_view_diagnostics(
            target_object=diagnostic_target,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            camera_name=None,
            focus_target=focus_target,
            view_name=view_name,
            orbit_horizontal=orbit_horizontal,
            orbit_vertical=orbit_vertical,
            zoom_factor=zoom_factor,
            persist_view=False,
        )
    except Exception:
        return None

    return build_view_diagnostics_hints(
        diagnostics_payload=diagnostics_payload,
        target_object=diagnostic_target,
        camera_name=None,
        focus_target=focus_target,
        view_name=view_name,
        orbit_horizontal=orbit_horizontal,
        orbit_vertical=orbit_vertical,
        zoom_factor=zoom_factor,
    )


def build_view_diagnostics_hints(
    *,
    diagnostics_payload: dict[str, Any] | None,
    target_object: str | None,
    camera_name: str | None,
    focus_target: str | None,
    view_name: str | None,
    orbit_horizontal: float,
    orbit_vertical: float,
    zoom_factor: float | None,
) -> list[ReferenceViewDiagnosticsHintContract]:
    if not isinstance(diagnostics_payload, dict):
        return []

    hints: list[ReferenceViewDiagnosticsHintContract] = []
    for item in list(diagnostics_payload.get("targets") or []):
        if not isinstance(item, dict):
            continue
        object_name = str(item.get("object_name") or "").strip()
        verdict = str(item.get("visibility_verdict") or "").strip()
        projection = item.get("projection") if isinstance(item.get("projection"), dict) else {}
        centered = bool(projection.get("centered")) if isinstance(projection, dict) else False
        raw_frame_coverage_ratio = projection.get("frame_coverage_ratio") if isinstance(projection, dict) else None
        frame_coverage_ratio: float | None
        if isinstance(raw_frame_coverage_ratio, (int, float)):
            frame_coverage_ratio = float(raw_frame_coverage_ratio)
        else:
            frame_coverage_ratio = None

        trigger: Literal["framing_ambiguity", "visibility_ambiguity", "occlusion_detected", "target_off_frame"] | None
        priority: Literal["high", "normal"] = "normal"
        reason: str | None = None

        if verdict == "fully_occluded":
            trigger = "occlusion_detected"
            priority = "high"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is currently fully occluded from this view. "
                "Call scene_view_diagnostics(...) before another compare/correction step so framing and occlusion are explicit."
            )
        elif verdict == "outside_frame":
            trigger = "target_off_frame"
            priority = "high"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is currently outside the frame. "
                "Call scene_view_diagnostics(...) before another compare/correction step so reframing is driven by typed view facts."
            )
        elif verdict == "partially_visible":
            trigger = "visibility_ambiguity"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is only partially visible from this view. "
                "Call scene_view_diagnostics(...) to inspect frame coverage and occlusion before another correction pass."
            )
        elif frame_coverage_ratio is not None and (frame_coverage_ratio < 0.999 or not centered):
            trigger = "framing_ambiguity"
            reason = (
                f"'{object_name or target_object or focus_target or 'target'}' is not cleanly centered/framed in the current view. "
                "Call scene_view_diagnostics(...) if the next decision depends on precise framing facts."
            )
        else:
            trigger = None

        if trigger is None or reason is None:
            continue

        arguments_hint: dict[str, object] = {
            "target_object": object_name or target_object or focus_target,
        }
        if camera_name:
            arguments_hint["camera_name"] = camera_name
        if focus_target:
            arguments_hint["focus_target"] = focus_target
        if view_name:
            arguments_hint["view_name"] = view_name
        if orbit_horizontal:
            arguments_hint["orbit_horizontal"] = orbit_horizontal
        if orbit_vertical:
            arguments_hint["orbit_vertical"] = orbit_vertical
        if zoom_factor is not None:
            arguments_hint["zoom_factor"] = zoom_factor

        hints.append(
            ReferenceViewDiagnosticsHintContract(
                hint_id=f"view_diag_{trigger}_{(object_name or 'target').lower()}",
                trigger=trigger,
                reason=reason,
                priority=priority,
                arguments_hint=arguments_hint,
            )
        )

    return hints
