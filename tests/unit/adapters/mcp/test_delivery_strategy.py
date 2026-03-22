"""Tests for structured-first delivery and compatibility policy."""

from server.adapters.mcp.contracts.compat import (
    CONTRACT_ENABLED_TOOLS,
    get_delivery_mode,
    should_prefer_native_structured_delivery,
)
from server.adapters.mcp.factory import build_server


def test_surface_profiles_expose_explicit_delivery_mode():
    """Each built surface should advertise its delivery policy explicitly."""

    legacy = build_server("legacy-flat")
    guided = build_server("llm-guided")

    assert legacy._bam_delivery_mode == "compatibility"
    assert guided._bam_delivery_mode == "structured_first"


def test_contract_enabled_tools_default_to_structured_first_delivery():
    """Contract-enabled tools should prefer native structured delivery by default."""

    assert "scene_context" in CONTRACT_ENABLED_TOOLS
    assert should_prefer_native_structured_delivery("llm-guided", "scene_context") is True
    assert should_prefer_native_structured_delivery("legacy-flat", "scene_context") is True


def test_non_contract_tools_do_not_implicitly_claim_structured_delivery():
    """Non-contract tools should remain outside the structured-first policy until migrated."""

    assert should_prefer_native_structured_delivery("llm-guided", "scene_get_viewport") is False
    assert get_delivery_mode("legacy-flat") == "compatibility"
