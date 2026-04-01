# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Runtime helpers for deterministic capture-bundle image generation."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Literal

from server.adapters.mcp.contracts.scene import SceneAssembledTargetScopeContract
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.infrastructure.tmp_paths import get_viewport_output_paths

CaptureStage = Literal["before", "after"]
CapturePresetProfile = Literal["compact", "rich"]


@dataclass(frozen=True, slots=True)
class CapturePresetSpec:
    """One deterministic viewport capture preset supported by the current runtime."""

    name: str
    width: int
    height: int
    shading: str = "SOLID"
    focus_target: bool = False
    isolate_target: bool = False
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


COMPACT_CAPTURE_PRESET_SPECS: tuple[CapturePresetSpec, ...] = (
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
        isolate_target=True,
        standard_view="FRONT",
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_side",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        standard_view="RIGHT",
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_top",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        standard_view="TOP",
        view_kind="focus",
    ),
)

RICH_CAPTURE_PRESET_SPECS: tuple[CapturePresetSpec, ...] = (
    CapturePresetSpec(
        name="context_wide",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=False,
        view_kind="wide",
    ),
    CapturePresetSpec(
        name="target_focus",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_oblique_left",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        orbit_horizontal=-35.0,
        orbit_vertical=15.0,
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_oblique_right",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        orbit_horizontal=35.0,
        orbit_vertical=15.0,
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_front",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        standard_view="FRONT",
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_side",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        standard_view="RIGHT",
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_top",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        standard_view="TOP",
        view_kind="focus",
    ),
    CapturePresetSpec(
        name="target_detail",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
        isolate_target=True,
        standard_view="FRONT",
        focus_zoom_factor=1.8,
        view_kind="focus",
    ),
)

CAPTURE_PRESET_PROFILES: dict[CapturePresetProfile, tuple[CapturePresetSpec, ...]] = {
    "compact": COMPACT_CAPTURE_PRESET_SPECS,
    "rich": RICH_CAPTURE_PRESET_SPECS,
}

DEFAULT_CAPTURE_PRESET_SPECS: tuple[CapturePresetSpec, ...] = COMPACT_CAPTURE_PRESET_SPECS


def resolve_capture_preset_specs(profile: CapturePresetProfile = "compact") -> tuple[CapturePresetSpec, ...]:
    """Return the deterministic preset set for a named capture profile."""

    return CAPTURE_PRESET_PROFILES[profile]


def capture_stage_images(
    scene_handler,
    *,
    bundle_id: str,
    stage: CaptureStage,
    target_object: str | None = None,
    target_objects: list[str] | tuple[str, ...] | None = None,
    preset_specs: tuple[CapturePresetSpec, ...] | None = None,
    preset_profile: CapturePresetProfile = "compact",
) -> list[VisionCaptureImageContract]:
    """Capture one deterministic stage view-set using the current viewport API."""

    resolved_preset_specs = preset_specs or resolve_capture_preset_specs(preset_profile)
    original_state = capture_scene_state(scene_handler)
    captures: list[VisionCaptureImageContract] = []
    try:
        normalized_target_objects = [name for name in list(target_objects or []) if str(name).strip()]
        isolate_names = normalized_target_objects or ([target_object] if target_object else [])
        for preset in resolved_preset_specs:
            focus_target = target_object if preset.focus_target else None
            if preset is not resolved_preset_specs[0]:
                restore_scene_state(scene_handler, original_state)
            if isolate_names and preset.isolate_target and hasattr(scene_handler, "isolate_object"):
                try:
                    scene_handler.isolate_object(isolate_names)
                except Exception:
                    pass
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
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None,
    truth_summary: dict | None = None,
) -> VisionCaptureBundleContract:
    """Build one deterministic before/after capture bundle contract."""

    preset_names = sorted(
        {capture.preset_name for capture in [*captures_before, *captures_after] if capture.preset_name is not None}
    )
    return VisionCaptureBundleContract(
        bundle_id=bundle_id,
        goal_id=goal_id,
        target_object=target_object,
        assembled_target_scope=assembled_target_scope,
        preset_names=preset_names,
        captures_before=captures_before,
        captures_after=captures_after,
        truth_summary=truth_summary,
    )
