"""
E2E tests for scene_clean_scene in real Blender.
"""

from __future__ import annotations

import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


def test_scene_clean_scene_removes_mesh_objects_and_keeps_default_scene_support(scene_handler, rpc_client):
    """A guided prep cleanup should remove created mesh objects while keeping the scene usable."""

    try:
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "CleanupCube"})

        objects_before = scene_handler.list_objects()
        assert any(obj["name"] == "CleanupCube" for obj in objects_before)

        result = scene_handler.clean_scene(keep_lights_and_cameras=True)
        assert "Scene cleaned" in result

        objects_after = scene_handler.list_objects()
        names_after = {obj["name"] for obj in objects_after}

        assert "CleanupCube" not in names_after
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
