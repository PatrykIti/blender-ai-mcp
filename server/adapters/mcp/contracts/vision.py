# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for TASK-121 vision/capture inputs."""

from __future__ import annotations

from typing import Any, Literal

from .base import MCPContract


class VisionCaptureImageContract(MCPContract):
    """One deterministic image artifact used in a capture bundle."""

    label: str
    image_path: str
    host_visible_path: str | None = None
    preset_name: str | None = None
    media_type: str = "image/png"
    view_kind: Literal["wide", "focus", "overlay", "reference"] = "wide"


class VisionCaptureBundleContract(MCPContract):
    """One before/after capture bundle prepared for bounded visual comparison."""

    bundle_id: str
    goal_id: str | None = None
    target_object: str | None = None
    preset_names: list[str]
    captures_before: list[VisionCaptureImageContract]
    captures_after: list[VisionCaptureImageContract]
    truth_summary: dict[str, Any] | None = None
