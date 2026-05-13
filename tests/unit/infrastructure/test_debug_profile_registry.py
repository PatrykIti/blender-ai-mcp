"""Tests for the shared repo-owned debug profile registry."""

from __future__ import annotations

import pytest
from server.infrastructure.debug_profiles import (
    DEFAULT_DEBUG_PROFILE_REGISTRY,
    debug_scope_enabled,
    parse_debug_selector,
    resolve_debug_profile_state,
    resolve_debug_profile_state_from_config,
    supported_debug_selector_values,
)


class _Config:
    def __init__(self, debug_selector, router_log_decisions: bool = True) -> None:
        self.BLENDER_AI_DEBUG = debug_selector
        self.ROUTER_LOG_DECISIONS = router_log_decisions


def test_supported_debug_selector_values_match_registry() -> None:
    assert supported_debug_selector_values() == (
        "off",
        "all",
        *DEFAULT_DEBUG_PROFILE_REGISTRY.scope_names,
    )


def test_parse_debug_selector_rejects_blank_items() -> None:
    with pytest.raises(ValueError, match="empty item"):
        parse_debug_selector("vision,,tools")


def test_resolve_debug_profile_state_uses_legacy_router_when_selector_unset() -> None:
    state = resolve_debug_profile_state(debug_selector=None, router_log_decisions=True)

    assert state.authoritative_selector is False
    assert state.router_legacy_compatibility is True
    assert state.enabled_scopes == frozenset({"router"})


def test_resolve_debug_profile_state_makes_selector_authoritative() -> None:
    state = resolve_debug_profile_state(debug_selector="tools", router_log_decisions=True)

    assert state.authoritative_selector is True
    assert state.router_legacy_compatibility is False
    assert state.enabled_scopes == frozenset({"tools"})


def test_resolve_debug_profile_state_from_config_disables_router_when_off() -> None:
    state = resolve_debug_profile_state_from_config(_Config(frozenset()))

    assert state.enabled_scopes == frozenset()
    assert debug_scope_enabled("router", config=_Config(frozenset())) is False


def test_debug_scope_enabled_honors_named_scope_selector() -> None:
    config = _Config(frozenset({"reference", "transport"}), router_log_decisions=True)

    assert debug_scope_enabled("reference", config=config) is True
    assert debug_scope_enabled("transport", config=config) is True
    assert debug_scope_enabled("router", config=config) is False
