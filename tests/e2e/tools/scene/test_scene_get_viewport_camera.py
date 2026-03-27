"""
E2E tests for camera-faithful scene_get_viewport behavior.
"""

from __future__ import annotations

import pytest

from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


def test_scene_get_viewport_uses_named_camera_perspective(scene_handler, rpc_client):
    """A named camera render should differ from USER_PERSPECTIVE when the camera is moved."""

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "ViewportCube"})

        # Create a deliberately different camera position from the default user view.
        scene_handler.create_camera(
            location=[0.0, -6.0, 0.75],
            rotation=[1.5708, 0.0, 0.0],
            name="E2E_RenderCamera",
        )

        user_view = scene_handler.get_viewport(
            width=320,
            height=240,
            shading="SOLID",
            camera_name="USER_PERSPECTIVE",
        )
        camera_view = scene_handler.get_viewport(
            width=320,
            height=240,
            shading="SOLID",
            camera_name="E2E_RenderCamera",
        )

        assert user_view
        assert camera_view
        assert camera_view != user_view
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
