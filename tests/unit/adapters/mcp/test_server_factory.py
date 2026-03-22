"""Tests for the FastMCP server factory composition root."""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from server.adapters.mcp.factory import build_server
from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.surfaces import SURFACE_PROFILES, get_surface_profile


def test_get_surface_profile_returns_expected_profiles():
    """Surface lookup should expose the baseline profile matrix."""

    assert set(SURFACE_PROFILES) == {
        "legacy-flat",
        "llm-guided",
        "internal-debug",
        "code-mode-pilot",
    }


def test_build_server_builds_default_surface():
    """Factory should build the default legacy-flat server surface."""

    server = build_server()

    assert isinstance(server, FastMCP)
    assert server._bam_surface_profile == "legacy-flat"
    assert server._bam_capability_manifest == get_capability_manifest()
    assert len(server.providers) >= 4


def test_build_server_builds_alternate_surface_profile():
    """Factory should build multiple surface profiles from reusable provider groups."""

    guided = build_server("llm-guided")
    debug = build_server("internal-debug")

    assert guided._bam_surface_profile == "llm-guided"
    assert debug._bam_surface_profile == "internal-debug"
    assert guided.name == get_surface_profile("llm-guided").server_name
    assert debug.name == get_surface_profile("internal-debug").server_name
    assert len(debug.providers) > len(guided.providers)


def test_factory_bootstrap_no_longer_imports_areas_side_effect_registry():
    """Server bootstrap should use the factory path instead of importing all areas for side effects."""

    server_source = Path("server/adapters/mcp/server.py").read_text(encoding="utf-8")

    assert "import server.adapters.mcp.areas" not in server_source
    assert "from server.adapters.mcp.instance import mcp" not in server_source
