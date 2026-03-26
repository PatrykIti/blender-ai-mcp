"""Tests for bounded vision capture policy helpers."""

from __future__ import annotations

from server.adapters.mcp.vision import choose_capture_preset_profile


def test_capture_profile_policy_defaults_to_compact_for_normal_budget():
    assert choose_capture_preset_profile(reference_image_count=0, max_images=8) == "compact"
    assert choose_capture_preset_profile(reference_image_count=2, max_images=10) == "compact"


def test_capture_profile_policy_promotes_to_rich_when_budget_allows():
    assert choose_capture_preset_profile(reference_image_count=1, max_images=17) == "rich"
    assert choose_capture_preset_profile(reference_image_count=2, max_images=18) == "rich"
