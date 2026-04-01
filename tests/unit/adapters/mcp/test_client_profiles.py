"""Tests for client profile presets and guided-mode defaults."""

from server.adapters.mcp.client_profiles import (
    get_client_profile_preset,
    list_client_profile_presets,
)
from server.adapters.mcp.session_phase import SessionPhase
from server.adapters.mcp.surfaces import SURFACE_PROFILES


def test_client_profile_presets_align_with_surface_profiles():
    """Every configured surface profile should have one preset record."""

    presets = {preset.name for preset in list_client_profile_presets()}

    assert presets == set(SURFACE_PROFILES)


def test_llm_guided_profile_uses_guided_mode_defaults():
    """llm-guided should carry the canonical first-pass guided-mode defaults."""

    preset = get_client_profile_preset("llm-guided")

    assert preset.guided_mode is True
    assert preset.default_phase == SessionPhase.BOOTSTRAP
    assert preset.entry_capability_ids == ("router", "workflow_catalog")
    assert preset.search_enabled_by_default is True


def test_legacy_manual_profile_stays_non_guided_and_router_free():
    """legacy-manual should expose a direct manual surface without router entry capabilities."""

    preset = get_client_profile_preset("legacy-manual")

    assert preset.guided_mode is False
    assert preset.entry_capability_ids == ()
    assert preset.search_enabled_by_default is False
