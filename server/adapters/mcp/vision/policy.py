# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Policy helpers for bounded vision runtime/capture behavior."""

from __future__ import annotations

from collections.abc import Sequence

from server.adapters.mcp.vision.capture_runtime import CapturePresetProfile


def choose_capture_preset_profile(
    *,
    reference_image_count: int,
    max_images: int,
) -> CapturePresetProfile:
    """Choose the deterministic capture profile for one bounded vision request."""

    compact_bundle_images = 4 * 2
    rich_bundle_images = 8 * 2
    required_reference_budget = max(1, reference_image_count)

    if max_images >= rich_bundle_images + required_reference_budget:
        return "rich"
    return "compact"


def infer_capture_preset_profile(preset_names: Sequence[str]) -> CapturePresetProfile:
    """Infer the effective capture profile from bundle preset names."""

    rich_only_names = {
        "target_focus",
        "target_oblique_left",
        "target_oblique_right",
        "target_detail",
    }
    if any(name in rich_only_names for name in preset_names):
        return "rich"
    return "compact"


def choose_reference_target_view(preset_names: Sequence[str]) -> str | None:
    """Choose the strongest target-view hint available from a bundle."""

    for candidate in ("target_focus", "target_front", "target_side", "target_top"):
        if candidate in preset_names:
            return candidate
    return None
