"""
E2E tests for scene_get_viewport in real Blender.
"""

from __future__ import annotations

import base64
import math

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


def test_scene_get_viewport_user_view_adjustment_restores_default_view(scene_handler):
    """Adjusted USER_PERSPECTIVE capture should restore the prior user view by default."""

    try:
        before_state = scene_handler.get_view_state()
        first = scene_handler.get_viewport(
            width=320,
            height=240,
            shading="SOLID",
            camera_name="USER_PERSPECTIVE",
        )
        adjusted = scene_handler.get_viewport(
            width=320,
            height=240,
            shading="SOLID",
            camera_name="USER_PERSPECTIVE",
            view_name="TOP",
        )
        third = scene_handler.get_viewport(
            width=320,
            height=240,
            shading="SOLID",
            camera_name="USER_PERSPECTIVE",
        )
        after_state = scene_handler.get_view_state()

        assert first
        assert adjusted
        assert adjusted != first
        assert third
        assert after_state.get("available") is True
        assert after_state.get("view_perspective") == before_state.get("view_perspective")
        assert math.isclose(
            float(after_state["view_distance"]), float(before_state["view_distance"]), rel_tol=0.0, abs_tol=1e-6
        )
        assert all(
            math.isclose(float(current), float(previous), rel_tol=0.0, abs_tol=1e-6)
            for current, previous in zip(after_state["view_location"], before_state["view_location"], strict=True)
        )
        assert all(
            math.isclose(float(current), float(previous), rel_tol=0.0, abs_tol=1e-6)
            for current, previous in zip(after_state["view_rotation"], before_state["view_rotation"], strict=True)
        )
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
