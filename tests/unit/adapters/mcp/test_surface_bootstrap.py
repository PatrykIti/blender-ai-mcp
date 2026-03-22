"""Regression tests for surface bootstrap behavior."""

from __future__ import annotations

import pytest
from server.adapters.mcp.factory import build_server


def test_default_surface_bootstrap_succeeds():
    """Default legacy-flat surface should bootstrap through the factory path."""

    server = build_server()

    assert server._bam_surface_profile == "legacy-flat"
    assert len(server.providers) >= 4


def test_invalid_surface_profile_fails_loudly():
    """Invalid surface profile should fail with a deterministic bootstrap error."""

    with pytest.raises(ValueError, match="Unknown MCP surface profile"):
        build_server("missing-profile")
