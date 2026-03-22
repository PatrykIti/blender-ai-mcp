"""Tests for component and payload pagination policy."""

from __future__ import annotations

from server.adapters.mcp.factory import build_server
from server.adapters.mcp.surfaces import get_surface_profile


def test_surface_profiles_keep_explicit_component_list_page_sizes():
    """Surface profiles should keep explicit component pagination policy."""

    legacy = get_surface_profile("legacy-flat")
    guided = get_surface_profile("llm-guided")
    debug = get_surface_profile("internal-debug")

    assert legacy.list_page_size == 100
    assert guided.list_page_size == 50
    assert debug.list_page_size == 100


def test_factory_applies_component_list_page_size_to_server():
    """Factory should propagate the configured list page size onto the built FastMCP server."""

    legacy = build_server("legacy-flat")
    guided = build_server("llm-guided")

    assert legacy._list_page_size == 100
    assert guided._list_page_size == 50
