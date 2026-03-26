# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Runtime helpers for deterministic capture-bundle image generation."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Literal

from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.infrastructure.tmp_paths import get_viewport_output_paths

CaptureStage = Literal["before", "after"]


@dataclass(frozen=True, slots=True)
class CapturePresetSpec:
    """One deterministic viewport capture preset supported by the current runtime."""

    name: str
    width: int
    height: int
    shading: str = "SOLID"
    focus_target: bool = False
    focus_zoom_factor: float = 1.0
    standard_view: Literal["FRONT", "RIGHT", "TOP"] | None = None
    orbit_horizontal: float | None = None
    orbit_vertical: float | None = None
    view_kind: Literal["wide", "focus"] = "wide"


@dataclass(frozen=True, slots=True)
class CaptureSceneState:
    """Internal reversible scene/view state used by capture orchestration."""

    visibility_snapshot: dict[str, bool] | None = None
    view_state: dict[str, Any] | None = None


DEFAULT_CAPTURE_PRESET_SPECS: tuple[CapturePresetSpec, ...] = (
    CapturePresetSpec(
        name="context_wide",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=False,
        view_kind="wide",
    ),
    CapturePresetSpec(
        name="target_front",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        standard_view="FRONT",
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_side",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        standard_view="RIGHT",
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_top",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        standard_view="TOP",
        view_kind="focus",
    ),
)


def capture_stage_images(
    scene_handler,
    *,
    bundle_id: str,
    stage: CaptureStage,
    target_object: str | None = None,
    preset_specs: tuple[CapturePresetSpec, ...] = DEFAULT_CAPTURE_PRESET_SPECS,
) -> list[VisionCaptureImageContract]:
    """Capture one deterministic stage view-set using the current viewport API."""

    original_state = capture_scene_state(scene_handler)
    captures: list[VisionCaptureImageContract] = []
    try:
        for preset in preset_specs:
            focus_target = target_object if preset.focus_target else None
            if preset is not preset_specs[0]:
                restore_scene_state(scene_handler, original_state)
            if preset.standard_view and hasattr(scene_handler, "set_standard_view"):
                try:
                    scene_handler.set_standard_view(preset.standard_view)
                except Exception:
                    pass
            if focus_target and hasattr(scene_handler, "camera_focus"):
                try:
                    scene_handler.camera_focus(focus_target, zoom_factor=preset.focus_zoom_factor)
                except Exception:
                    pass

            if focus_target and (preset.orbit_horizontal is not None or preset.orbit_vertical is not None):
                if hasattr(scene_handler, "camera_orbit"):
                    try:
                        scene_handler.camera_orbit(
                            angle_horizontal=float(preset.orbit_horizontal or 0.0),
                            angle_vertical=float(preset.orbit_vertical or 0.0),
                            target_object=focus_target,
                        )
                    except Exception:
                        pass
            b64_data = scene_handler.get_viewport(
                width=preset.width,
                height=preset.height,
                shading=preset.shading,
                camera_name=None,
                focus_target=focus_target,
            )
            filename = f"{bundle_id}_{stage}_{preset.name}.jpg"
            latest_name = f"{bundle_id}_{stage}_{preset.name}_latest.jpg"
            internal_file, _internal_latest, external_file, _external_latest = get_viewport_output_paths(
                filename,
                latest_name=latest_name,
            )
            internal_file.write_bytes(base64.b64decode(b64_data))

            captures.append(
                VisionCaptureImageContract(
                    label=f"{preset.name}_{stage}",
                    image_path=str(internal_file),
                    host_visible_path=external_file,
                    preset_name=preset.name,
                    media_type="image/jpeg",
                    view_kind=preset.view_kind,
                )
            )
    finally:
        restore_scene_state(scene_handler, original_state)

    return captures


def capture_scene_state(scene_handler) -> CaptureSceneState:
    """Capture best-effort reversible scene/view state for bounded capture flows.

    Current scaffold stores visibility from `snapshot_state()` when available and
    leaves `view_state` empty until a dedicated view-state helper exists.
    """

    visibility_snapshot: dict[str, bool] | None = None
    try:
        snapshot = scene_handler.snapshot_state(include_mesh_stats=False, include_materials=False)
        raw_snapshot = snapshot.get("snapshot", snapshot) if isinstance(snapshot, dict) else {}
        objects = raw_snapshot.get("objects", []) if isinstance(raw_snapshot, dict) else []
        if isinstance(objects, list):
            visibility_snapshot = {
                str(item["name"]): bool(item.get("visible", True))
                for item in objects
                if isinstance(item, dict) and "name" in item
            }
    except Exception:
        visibility_snapshot = None

    view_state: dict[str, Any] | None = None
    try:
        if hasattr(scene_handler, "get_view_state"):
            candidate = scene_handler.get_view_state()
            if isinstance(candidate, dict) and candidate.get("available") is True:
                view_state = candidate
    except Exception:
        view_state = None

    return CaptureSceneState(
        visibility_snapshot=visibility_snapshot,
        view_state=view_state,
    )


def restore_scene_state(scene_handler, state: CaptureSceneState) -> None:
    """Best-effort restore for bounded capture orchestration side effects.

    Current scaffold restores visibility only. View-state restoration remains an
    explicit future step once a dedicated internal helper exists.
    """

    if state.view_state and hasattr(scene_handler, "restore_view_state"):
        try:
            scene_handler.restore_view_state(state.view_state)
        except Exception:
            pass

    if state.visibility_snapshot:
        for object_name, visible in state.visibility_snapshot.items():
            try:
                scene_handler.hide_object(object_name, hide=not visible, hide_render=False)
            except Exception:
                continue


def build_capture_bundle(
    *,
    bundle_id: str,
    target_object: str | None,
    captures_before: list[VisionCaptureImageContract],
    captures_after: list[VisionCaptureImageContract],
    goal_id: str | None = None,
    truth_summary: dict | None = None,
) -> VisionCaptureBundleContract:
    """Build one deterministic before/after capture bundle contract."""

    preset_names = sorted(
        {
            capture.preset_name
            for capture in [*captures_before, *captures_after]
            if capture.preset_name is not None
        }
    )
    return VisionCaptureBundleContract(
        bundle_id=bundle_id,
        goal_id=goal_id,
        target_object=target_object,
        preset_names=preset_names,
        captures_before=captures_before,
        captures_after=captures_after,
        truth_summary=truth_summary,
    )
