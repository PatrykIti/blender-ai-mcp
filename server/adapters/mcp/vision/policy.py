# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Policy helpers for bounded vision runtime/capture behavior."""

from __future__ import annotations

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
