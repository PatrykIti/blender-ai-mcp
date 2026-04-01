"""Compatibility-focused regression tests for public surface coexistence."""

from __future__ import annotations

from server.adapters.mcp.factory import build_server


def test_legacy_flat_and_llm_guided_share_same_manifest():
    """Current coexistence-safe surfaces should boot from the same capability manifest."""

    legacy = build_server("legacy-flat")
    guided = build_server("llm-guided")

    assert legacy._bam_capability_manifest == guided._bam_capability_manifest
    assert legacy._bam_transform_pipeline == guided._bam_transform_pipeline


def test_internal_debug_surface_keeps_extra_provider_capacity():
    """Internal/debug surfaces may expose a larger provider stack without changing the manifest."""

    guided = build_server("llm-guided")
    debug = build_server("internal-debug")

    assert len(debug.providers) > len(guided.providers)
    assert debug._bam_capability_manifest == guided._bam_capability_manifest
