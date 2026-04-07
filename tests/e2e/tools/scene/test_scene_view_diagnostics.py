"""
E2E tests for scene_view_diagnostics in real Blender.
"""

from __future__ import annotations

import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


def test_scene_view_diagnostics_reports_named_camera_projection(scene_handler, rpc_client):
    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "ViewportCube"})
        scene_handler.create_camera(
            location=[0.0, -6.0, 1.0],
            rotation=[1.5708, 0.0, 0.0],
            name="DiagCamera",
        )

        result = scene_handler.get_view_diagnostics(
            target_object="ViewportCube",
            camera_name="DiagCamera",
        )

        assert result["view_query"]["requested_view_source"] == "named_camera"
        assert result["view_query"]["available"] is True
        assert result["summary"]["target_count"] == 1
        assert result["targets"][0]["projection_status"] in {"projected", "outside_frame", "behind_view"}
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_scene_view_diagnostics_user_view_adjustment_restores_state(scene_handler, rpc_client):
    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "ViewportCube"})

        result = scene_handler.get_view_diagnostics(
            target_object="ViewportCube",
            camera_name="USER_PERSPECTIVE",
            view_name="TOP",
        )

        assert result["view_query"]["requested_view_source"] == "user_perspective"
        assert result["view_query"]["state_restored"] is True
        assert result["summary"]["target_count"] == 1
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
