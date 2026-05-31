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
    VisionObjectIdCaptureArtifactContract,
    VisionOverlayMarkContract,
)
from server.infrastructure.tmp_paths import get_viewport_output_paths

from .marks import build_object_mark_overlay

CaptureStage = Literal["before", "after"]
CapturePresetProfile = Literal["compact", "rich"]
AuxiliaryCaptureKind = Literal["depth", "normal", "object_id"]
DEFAULT_AUXILIARY_CAPTURE_KINDS: tuple[AuxiliaryCaptureKind, ...] = ("depth", "normal", "object_id")


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


# Bounded set of known view-op failure markers. Headless Blender returns these
# strings instead of raising, so a failed op would otherwise be discarded and the
# mislabeled view would reach the VLM as trustworthy. Success-confirmation
# strings (e.g. "Set 3D viewport to FRONT view") are intentionally not markers.
_KNOWN_VIEW_OP_FAILURE_MARKERS = (
    "no 3d viewport found",
    "requires an active 3d view",
    "no active 3d view",
    "no 3d view",
)


def _normalize_object_id_index_map(index_map: object) -> dict[int, str]:
    if not isinstance(index_map, dict):
        return {}
    normalized: dict[int, str] = {}
    for raw_index, raw_name in index_map.items():
        try:
            index = int(raw_index)
        except (TypeError, ValueError):
            continue
        name = str(raw_name or "").strip()
        if index <= 0 or not name:
            continue
        normalized[index] = name
    return normalized


def _normalize_missing_objects(raw_missing: object) -> list[str]:
    if not isinstance(raw_missing, list):
        return []
    return [str(item).strip() for item in raw_missing if str(item).strip()]


def _normalize_auxiliary_capture_kinds(
    raw_kinds: set[str] | list[str] | tuple[str, ...] | None,
) -> tuple[AuxiliaryCaptureKind, ...]:
    if raw_kinds is None:
        return DEFAULT_AUXILIARY_CAPTURE_KINDS
    requested = {str(kind).strip().lower() for kind in raw_kinds if str(kind).strip()}
    return tuple(kind for kind in DEFAULT_AUXILIARY_CAPTURE_KINDS if kind in requested)


def _object_id_artifact_unavailable(
    *,
    warning: str,
    index_map: dict[int, str] | None = None,
    missing_objects: list[str] | None = None,
) -> VisionObjectIdCaptureArtifactContract:
    return VisionObjectIdCaptureArtifactContract(
        index_map=index_map or {},
        missing_objects=missing_objects or [],
        capture_ok=False,
        capture_warning=warning[:240],
    )


def _write_auxiliary_capture(
    *,
    bundle_id: str,
    stage: CaptureStage,
    preset: CapturePresetSpec,
    view_kind: AuxiliaryCaptureKind,
    image_bytes: bytes,
    source_path: str | None = None,
    source_host_visible_path: str | None = None,
) -> VisionCaptureImageContract:
    label = f"{preset.name}_{stage}_{view_kind}"
    if source_path:
        return VisionCaptureImageContract(
            label=label,
            image_path=source_path,
            host_visible_path=source_host_visible_path,
            preset_name=preset.name,
            media_type="image/png",
            view_kind=view_kind,
        )

    filename = f"{bundle_id}_{stage}_{preset.name}_{view_kind}.png"
    latest_name = f"{bundle_id}_{stage}_{preset.name}_{view_kind}_latest.png"
    internal_file, _internal_latest, external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    internal_file.write_bytes(image_bytes)
    return VisionCaptureImageContract(
        label=label,
        image_path=str(internal_file),
        host_visible_path=external_file,
        preset_name=preset.name,
        media_type="image/png",
        view_kind=view_kind,
    )


def _decode_png_pass_result(result: object, *, method_name: str) -> bytes | None:
    if not isinstance(result, str):
        return None
    image_b64 = result.strip()
    if not image_b64 or image_b64.startswith(method_name):
        return None
    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except Exception:
        return None
    return image_bytes if image_bytes.startswith(b"\x89PNG\r\n\x1a\n") else None


def _capture_auxiliary_pass(
    scene_handler,
    *,
    bundle_id: str,
    stage: CaptureStage,
    preset: CapturePresetSpec,
    view_kind: AuxiliaryCaptureKind,
    object_id_artifact: VisionObjectIdCaptureArtifactContract | None = None,
) -> VisionCaptureImageContract | None:
    if view_kind == "object_id":
        if object_id_artifact is None or not object_id_artifact.capture_ok or object_id_artifact.image_path is None:
            return None
        return _write_auxiliary_capture(
            bundle_id=bundle_id,
            stage=stage,
            preset=preset,
            view_kind=view_kind,
            image_bytes=b"",
            source_path=object_id_artifact.image_path,
            source_host_visible_path=object_id_artifact.host_visible_path,
        )

    method_name = "get_depth_pass" if view_kind == "depth" else "get_normal_pass"
    if not hasattr(scene_handler, method_name):
        return None
    try:
        method = getattr(scene_handler, method_name)
        result = method(width=preset.width, height=preset.height, camera_name="USER_PERSPECTIVE")
    except Exception:
        return None
    image_bytes = _decode_png_pass_result(result, method_name=method_name)
    if image_bytes is None:
        return None
    return _write_auxiliary_capture(
        bundle_id=bundle_id,
        stage=stage,
        preset=preset,
        view_kind=view_kind,
        image_bytes=image_bytes,
    )


def _capture_mark_overlay(
    scene_handler,
    *,
    bundle_id: str,
    stage: CaptureStage,
    preset: CapturePresetSpec,
    object_names: list[str],
    base_image_path: str,
) -> VisionCaptureImageContract | None:
    if not object_names:
        return None
    ordered_object_names = sorted(dict.fromkeys(object_names))

    filename = f"{bundle_id}_{stage}_{preset.name}_overlay.jpg"
    latest_name = f"{bundle_id}_{stage}_{preset.name}_overlay_latest.jpg"
    internal_file, _internal_latest, external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    try:
        overlay_path, mark_id_to_object = build_object_mark_overlay(
            scene_handler,
            object_names=ordered_object_names,
            base_image_path=base_image_path,
            output_path=str(internal_file),
            output_dir=str(internal_file.parent),
            view_name=None,
            width=preset.width,
            height=preset.height,
        )
    except Exception:
        return None
    if overlay_path is None or not mark_id_to_object:
        return None
    return VisionCaptureImageContract(
        label=f"{preset.name}_{stage}_overlay",
        image_path=overlay_path,
        host_visible_path=external_file,
        preset_name=preset.name,
        media_type="image/jpeg",
        view_kind="overlay",
        overlay_marks=[
            VisionOverlayMarkContract(
                mark_id=mark_id,
                object_name=object_name,
                status="placed" if mark_id_to_object.get(mark_id) == object_name else "unmarked",
            )
            for mark_id, object_name in enumerate(ordered_object_names, start=1)
        ],
    )


def _capture_object_id_artifact(
    scene_handler,
    *,
    bundle_id: str,
    stage: CaptureStage,
    preset: CapturePresetSpec,
    object_names: list[str],
) -> VisionObjectIdCaptureArtifactContract | None:
    """Render one USER_PERSPECTIVE object-ID sidecar for an already-framed view."""

    if not object_names:
        return None
    if not hasattr(scene_handler, "get_object_id_pass"):
        return _object_id_artifact_unavailable(warning="get_object_id_pass is unavailable on this scene handler.")

    try:
        result = scene_handler.get_object_id_pass(
            object_names=list(dict.fromkeys(object_names)),
            width=preset.width,
            height=preset.height,
            camera_name="USER_PERSPECTIVE",
        )
    except Exception as exc:
        return _object_id_artifact_unavailable(warning=f"get_object_id_pass raised: {exc!r}")

    if isinstance(result, str):
        return _object_id_artifact_unavailable(warning=f"get_object_id_pass: {result}")
    if not isinstance(result, dict):
        return _object_id_artifact_unavailable(
            warning=f"get_object_id_pass returned unsupported {type(result).__name__} result."
        )

    index_map = _normalize_object_id_index_map(result.get("index_map"))
    missing_objects = _normalize_missing_objects(result.get("missing"))
    image_b64 = str(result.get("image") or "").strip()
    if not image_b64:
        return _object_id_artifact_unavailable(
            warning="get_object_id_pass returned no object-ID image.",
            index_map=index_map,
            missing_objects=missing_objects,
        )

    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except Exception as exc:
        return _object_id_artifact_unavailable(
            warning=f"get_object_id_pass returned invalid base64 PNG data: {exc!r}",
            index_map=index_map,
            missing_objects=missing_objects,
        )

    filename = f"{bundle_id}_{stage}_{preset.name}_object_id.png"
    latest_name = f"{bundle_id}_{stage}_{preset.name}_object_id_latest.png"
    internal_file, _internal_latest, external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    internal_file.write_bytes(image_bytes)
    return VisionObjectIdCaptureArtifactContract(
        image_path=str(internal_file),
        host_visible_path=external_file,
        index_map=index_map,
        missing_objects=missing_objects,
        capture_ok=bool(index_map),
        capture_warning=None if index_map else "get_object_id_pass returned an empty object-ID index map.",
    )


def _should_capture_object_id_for_preset(
    preset: CapturePresetSpec,
    *,
    include_object_id_pass: bool,
    object_id_preset_names: set[str],
    object_id_attempted: bool,
) -> bool:
    if not include_object_id_pass or preset.view_kind != "focus":
        return False
    if object_id_preset_names:
        return preset.name in object_id_preset_names
    if preset.name == "target_front":
        return True
    return not object_id_attempted


def _should_capture_auxiliary_for_preset(
    preset: CapturePresetSpec,
    *,
    include_auxiliary_passes: bool,
    auxiliary_preset_names: set[str],
    auxiliary_attempted: bool,
) -> bool:
    if not include_auxiliary_passes or preset.view_kind != "focus":
        return False
    if auxiliary_preset_names:
        return preset.name in auxiliary_preset_names
    if preset.name == "target_front":
        return True
    return not auxiliary_attempted


def _should_capture_mark_overlay_for_preset(
    preset: CapturePresetSpec,
    *,
    include_mark_overlay: bool,
    mark_overlay_preset_names: set[str],
    mark_overlay_attempted: bool,
) -> bool:
    if not include_mark_overlay or preset.view_kind != "focus":
        return False
    if mark_overlay_preset_names:
        return preset.name in mark_overlay_preset_names
    if preset.name == "target_front":
        return True
    return not mark_overlay_attempted


def _classify_view_op_result(op_name: str, result: object) -> str | None:
    """Return a short failure note when a view-op result signals a known failure.

    Returns ``None`` for success confirmations and non-string results so the
    common case (handlers that return human-readable confirmation strings) is not
    misread as a failure. Adding a new handler failure phrase is a one-line change
    to ``_KNOWN_VIEW_OP_FAILURE_MARKERS``.
    """

    if not isinstance(result, str):
        return None
    lowered = result.strip().lower()
    if not lowered:
        return None
    for marker in _KNOWN_VIEW_OP_FAILURE_MARKERS:
        if marker in lowered:
            return f"{op_name}: {result.strip()}"
    return None


def capture_stage_images(
    scene_handler,
    *,
    bundle_id: str,
    stage: CaptureStage,
    target_object: str | None = None,
    target_objects: list[str] | tuple[str, ...] | None = None,
    preset_specs: tuple[CapturePresetSpec, ...] | None = None,
    preset_profile: CapturePresetProfile = "compact",
    include_object_id_pass: bool = False,
    object_id_preset_names: set[str] | list[str] | tuple[str, ...] | None = None,
    include_auxiliary_passes: bool = False,
    auxiliary_preset_names: set[str] | list[str] | tuple[str, ...] | None = None,
    auxiliary_view_kinds: set[str] | list[str] | tuple[str, ...] | None = None,
    include_mark_overlay: bool = False,
    mark_overlay_preset_names: set[str] | list[str] | tuple[str, ...] | None = None,
) -> list[VisionCaptureImageContract]:
    """Capture one deterministic stage view-set using the current viewport API."""

    resolved_preset_specs = preset_specs or resolve_capture_preset_specs(preset_profile)
    normalized_object_id_preset_names = {
        str(name).strip() for name in list(object_id_preset_names or []) if str(name).strip()
    }
    normalized_auxiliary_preset_names = {
        str(name).strip() for name in list(auxiliary_preset_names or []) if str(name).strip()
    }
    normalized_mark_overlay_preset_names = {
        str(name).strip() for name in list(mark_overlay_preset_names or []) if str(name).strip()
    }
    normalized_auxiliary_view_kinds = _normalize_auxiliary_capture_kinds(auxiliary_view_kinds)
    original_state = capture_scene_state(scene_handler)
    captures: list[VisionCaptureImageContract] = []
    object_id_attempted = False
    auxiliary_attempted = False
    mark_overlay_attempted = False
    try:
        normalized_target_objects = [name for name in list(target_objects or []) if str(name).strip()]
        isolate_names = normalized_target_objects or ([target_object] if target_object else [])
        for preset in resolved_preset_specs:
            focus_target = target_object if preset.focus_target else None
            preset_warnings: list[str] = []
            if preset is not resolved_preset_specs[0]:
                restore_scene_state(scene_handler, original_state)
            if isolate_names and preset.isolate_target and hasattr(scene_handler, "isolate_object"):
                try:
                    result = scene_handler.isolate_object(isolate_names)
                    note = _classify_view_op_result("isolate_object", result)
                    if note is not None:
                        preset_warnings.append(note)
                except Exception as exc:  # keep capture reversible; record instead of discard
                    preset_warnings.append(f"isolate_object raised: {exc!r}")
            if preset.standard_view and hasattr(scene_handler, "set_standard_view"):
                try:
                    result = scene_handler.set_standard_view(preset.standard_view)
                    note = _classify_view_op_result(f"set_standard_view({preset.standard_view})", result)
                    if note is not None:
                        preset_warnings.append(note)
                except Exception as exc:
                    preset_warnings.append(f"set_standard_view raised: {exc!r}")
            if focus_target and hasattr(scene_handler, "camera_focus"):
                try:
                    result = scene_handler.camera_focus(focus_target, zoom_factor=preset.focus_zoom_factor)
                    note = _classify_view_op_result("camera_focus", result)
                    if note is not None:
                        preset_warnings.append(note)
                except Exception as exc:
                    preset_warnings.append(f"camera_focus raised: {exc!r}")

            if focus_target and (preset.orbit_horizontal is not None or preset.orbit_vertical is not None):
                if hasattr(scene_handler, "camera_orbit"):
                    try:
                        result = scene_handler.camera_orbit(
                            angle_horizontal=float(preset.orbit_horizontal or 0.0),
                            angle_vertical=float(preset.orbit_vertical or 0.0),
                            target_object=focus_target,
                        )
                        note = _classify_view_op_result("camera_orbit", result)
                        if note is not None:
                            preset_warnings.append(note)
                    except Exception as exc:
                        preset_warnings.append(f"camera_orbit raised: {exc!r}")
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

            capture_label = f"{preset.name}_{stage}"
            capture_warning = f"{capture_label}: " + "; ".join(preset_warnings) if preset_warnings else None
            object_id_artifact = None
            auxiliary_enabled = _should_capture_auxiliary_for_preset(
                preset,
                include_auxiliary_passes=include_auxiliary_passes,
                auxiliary_preset_names=normalized_auxiliary_preset_names,
                auxiliary_attempted=auxiliary_attempted,
            )
            if _should_capture_object_id_for_preset(
                preset,
                include_object_id_pass=include_object_id_pass
                or (auxiliary_enabled and "object_id" in normalized_auxiliary_view_kinds),
                object_id_preset_names=normalized_object_id_preset_names,
                object_id_attempted=object_id_attempted,
            ):
                object_id_attempted = True
                object_id_artifact = _capture_object_id_artifact(
                    scene_handler,
                    bundle_id=bundle_id,
                    stage=stage,
                    preset=preset,
                    object_names=list(isolate_names),
                )
            primary_capture = VisionCaptureImageContract(
                label=capture_label,
                image_path=str(internal_file),
                host_visible_path=external_file,
                preset_name=preset.name,
                media_type="image/jpeg",
                view_kind=preset.view_kind,
                capture_ok=not preset_warnings,
                capture_warning=capture_warning,
                object_id_artifact=object_id_artifact,
            )
            captures.append(primary_capture)
            if auxiliary_enabled:
                auxiliary_attempted = True
                captures.extend(
                    capture
                    for capture in (
                        _capture_auxiliary_pass(
                            scene_handler,
                            bundle_id=bundle_id,
                            stage=stage,
                            preset=preset,
                            view_kind=view_kind,
                            object_id_artifact=object_id_artifact,
                        )
                        for view_kind in normalized_auxiliary_view_kinds
                    )
                    if capture is not None
                )
            if _should_capture_mark_overlay_for_preset(
                preset,
                include_mark_overlay=include_mark_overlay,
                mark_overlay_preset_names=normalized_mark_overlay_preset_names,
                mark_overlay_attempted=mark_overlay_attempted,
            ):
                mark_overlay_attempted = True
                overlay_capture = _capture_mark_overlay(
                    scene_handler,
                    bundle_id=bundle_id,
                    stage=stage,
                    preset=preset,
                    object_names=list(isolate_names),
                    base_image_path=str(internal_file),
                )
                if overlay_capture is not None:
                    captures.append(overlay_capture)
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
    capture_warnings = [
        capture.capture_warning
        for capture in [*captures_before, *captures_after]
        if capture.capture_warning is not None
    ]
    capture_warnings.extend(
        artifact.capture_warning
        for capture in [*captures_before, *captures_after]
        if (artifact := capture.object_id_artifact) is not None and artifact.capture_warning is not None
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
        capture_warnings=capture_warnings,
    )
