"""
E2E tests for the deterministic Z-depth render pass (TASK-179-01).
"""

from __future__ import annotations

import base64

import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


def _looks_like_png(data: str) -> bool:
    try:
        raw = base64.b64decode(data)
    except Exception:
        return False
    # PNG magic number.
    return raw[:8] == b"\x89PNG\r\n\x1a\n" and len(raw) > 100


def test_scene_get_depth_pass_returns_png_for_named_camera(scene_handler, rpc_client):
    """A depth pass for a named camera over a real cube returns a non-trivial PNG."""

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "DepthCube"})
        scene_handler.create_camera(
            location=[0.0, -6.0, 0.75],
            rotation=[1.5708, 0.0, 0.0],
            name="E2E_DepthCamera",
        )

        depth = scene_handler.get_depth_pass(width=320, height=240, camera_name="E2E_DepthCamera")

        assert depth, "depth pass returned empty result"
        assert _looks_like_png(depth), "depth pass result is not a valid PNG"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_scene_get_depth_pass_is_reversible(scene_handler, rpc_client):
    """The depth pass must restore the render engine/resolution/format it mutates.

    Comparing rendered image bytes is unreliable (Blender stamps each render with a
    timestamp), so reversibility is checked against the deterministic render
    settings the depth pass touches.
    """

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "DepthCube2"})
        scene_handler.create_camera(location=[0.0, -6.0, 0.75], rotation=[1.5708, 0.0, 0.0], name="E2E_DepthCamera2")

        before = scene_handler.inspect_render_settings()
        depth = scene_handler.get_depth_pass(width=320, height=240, camera_name="E2E_DepthCamera2")
        after = scene_handler.inspect_render_settings()

        assert depth and _looks_like_png(depth)
        # The render engine, resolution, and image format the depth pass mutates
        # must all be restored to their pre-pass values.
        assert after["render_engine"] == before["render_engine"], "render engine not restored"
        assert after["resolution"] == before["resolution"], "resolution not restored"
        assert after["image_settings"]["file_format"] == before["image_settings"]["file_format"], (
            "image file format not restored"
        )
        assert after["image_settings"]["color_mode"] == before["image_settings"]["color_mode"], (
            "image color mode not restored"
        )
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_scene_get_depth_pass_reports_missing_camera(scene_handler, rpc_client):
    """An unknown camera name yields a clear error string, not a crash."""

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        result = scene_handler.get_depth_pass(width=160, height=120, camera_name="NoSuchCamera")
        assert "not found" in result.lower()
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
