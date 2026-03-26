# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Runtime helpers for deterministic capture-bundle image generation."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Literal

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
    view_kind: Literal["wide", "focus"] = "wide"


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
        name="target_focus",
        width=1280,
        height=960,
        shading="SOLID",
        focus_target=True,
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

    captures: list[VisionCaptureImageContract] = []

    for preset in preset_specs:
        focus_target = target_object if preset.focus_target else None
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

    return captures


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
