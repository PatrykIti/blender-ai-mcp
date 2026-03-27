"""
E2E tests for scene_get_viewport in real Blender.
"""

from __future__ import annotations

import base64

import pytest

from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


def test_scene_get_viewport_returns_decodable_base64(scene_handler):
    """Viewport capture should produce real image bytes in Blender-backed execution."""

    try:
        payload = scene_handler.get_viewport(width=320, height=240, shading="SOLID")
        decoded = base64.b64decode(payload, validate=True)

        assert decoded
        assert len(decoded) > 100
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
