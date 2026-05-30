# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for TASK-121 vision/capture inputs."""

from __future__ import annotations

from typing import Any, Literal

from .base import MCPContract
from .scene import SceneAssembledTargetScopeContract


class VisionCaptureImageContract(MCPContract):
    """One deterministic image artifact used in a capture bundle."""

    label: str
    image_path: str
    host_visible_path: str | None = None
    preset_name: str | None = None
    media_type: str = "image/png"
    view_kind: Literal["wide", "focus", "overlay", "reference"] = "wide"
    capture_ok: bool = True
    """Advisory reliability flag: ``False`` when a camera/view op for this preset
    returned a known failure marker, so the framed view may not match its label.
    Defaults to ``True`` so existing serialized payloads stay valid."""
    capture_warning: str | None = None
    """Short advisory note naming which view op failed and the preset it was
    meant to produce; ``None`` on a clean capture."""


class VisionCaptureBundleContract(MCPContract):
    """One before/after capture bundle prepared for bounded visual comparison."""

    bundle_id: str
    goal_id: str | None = None
    target_object: str | None = None
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None
    preset_names: list[str]
    captures_before: list[VisionCaptureImageContract]
    captures_after: list[VisionCaptureImageContract]
    truth_summary: dict[str, Any] | None = None
    capture_warnings: list[str] = []
    """Advisory bundle-level summary of per-image capture failures across both
    stages; empty when every capture in the bundle framed cleanly."""
