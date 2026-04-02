"""Tests for structured-first delivery and compatibility policy."""

from server.adapters.mcp.contracts.compat import (
    CONTRACT_ENABLED_TOOLS,
    get_delivery_mode,
    should_prefer_native_structured_delivery,
)
from server.adapters.mcp.factory import build_server


def test_surface_profiles_expose_explicit_delivery_mode():
    """Each built surface should advertise its delivery policy explicitly."""

    manual = build_server("legacy-manual")
    legacy = build_server("legacy-flat")
    guided = build_server("llm-guided")

    assert manual._bam_delivery_mode == "compatibility"
    assert legacy._bam_delivery_mode == "compatibility"
    assert guided._bam_delivery_mode == "structured_first"


def test_contract_enabled_tools_default_to_structured_first_delivery():
    """Contract-enabled tools should prefer native structured delivery by default."""

    assert "scene_context" in CONTRACT_ENABLED_TOOLS
    assert "macro_cutout_recess" in CONTRACT_ENABLED_TOOLS
    assert "macro_finish_form" in CONTRACT_ENABLED_TOOLS
    assert "macro_relative_layout" in CONTRACT_ENABLED_TOOLS
    assert "macro_attach_part_to_surface" in CONTRACT_ENABLED_TOOLS
    assert "macro_align_part_with_contact" in CONTRACT_ENABLED_TOOLS
    assert "macro_place_symmetry_pair" in CONTRACT_ENABLED_TOOLS
    assert "macro_adjust_relative_proportion" in CONTRACT_ENABLED_TOOLS
    assert "scene_create" in CONTRACT_ENABLED_TOOLS
    assert "scene_configure" in CONTRACT_ENABLED_TOOLS
    assert "mesh_select" in CONTRACT_ENABLED_TOOLS
    assert "mesh_select_targeted" in CONTRACT_ENABLED_TOOLS
    assert should_prefer_native_structured_delivery("llm-guided", "scene_context") is True
    assert should_prefer_native_structured_delivery("llm-guided", "macro_cutout_recess") is True
    assert should_prefer_native_structured_delivery("llm-guided", "macro_finish_form") is True
    assert should_prefer_native_structured_delivery("llm-guided", "macro_relative_layout") is True
    assert should_prefer_native_structured_delivery("llm-guided", "macro_attach_part_to_surface") is True
    assert should_prefer_native_structured_delivery("llm-guided", "macro_align_part_with_contact") is True
    assert should_prefer_native_structured_delivery("llm-guided", "macro_place_symmetry_pair") is True
    assert should_prefer_native_structured_delivery("llm-guided", "macro_adjust_relative_proportion") is True
    assert should_prefer_native_structured_delivery("llm-guided", "scene_create") is True
    assert should_prefer_native_structured_delivery("llm-guided", "scene_configure") is True
    assert should_prefer_native_structured_delivery("llm-guided", "mesh_select") is True
    assert should_prefer_native_structured_delivery("legacy-flat", "scene_context") is True


def test_non_contract_tools_do_not_implicitly_claim_structured_delivery():
    """Non-contract tools should remain outside the structured-first policy until migrated."""

    assert should_prefer_native_structured_delivery("llm-guided", "scene_get_viewport") is False
    assert get_delivery_mode("legacy-manual") == "compatibility"
    assert get_delivery_mode("legacy-flat") == "compatibility"
