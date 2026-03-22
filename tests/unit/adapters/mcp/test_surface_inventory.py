"""Regression tests for surface inventory and manifest behavior."""

from __future__ import annotations

from server.adapters.mcp.factory import build_server
from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.surfaces import get_surface_profile


def test_surface_provider_count_matches_profile_definition():
    """Booted surfaces should expose the provider stack implied by the selected profile."""

    surface = get_surface_profile("internal-debug")
    server = build_server("internal-debug")

    # FastMCP adds one default LocalProvider alongside explicit providers.
    assert len(server.providers) == len(surface.provider_builders) + 1


def test_surface_manifest_matches_platform_scaffold():
    """Every booted surface should carry the same platform-owned manifest scaffold."""

    server = build_server("llm-guided")
    manifest = get_capability_manifest()

    assert server._bam_capability_manifest == manifest
    assert any(entry.capability_id == "text" for entry in manifest)
    assert any(entry.capability_id == "workflow_catalog" for entry in manifest)
