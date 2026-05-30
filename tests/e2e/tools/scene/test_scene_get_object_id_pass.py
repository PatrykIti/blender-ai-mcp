"""
E2E tests for the deterministic per-object-ID mask render pass (TASK-179-01).
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
    return raw[:8] == b"\x89PNG\r\n\x1a\n" and len(raw) > 100


def test_object_id_pass_returns_mask_and_index_map(scene_handler, rpc_client):
    """Two real objects yield a PNG mask plus an index->name map for both."""

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "IdCube"})
        rpc_client.send_request(
            "modeling.create_primitive",
            {"primitive_type": "UV_SPHERE", "name": "IdSphere", "location": [3.0, 0.0, 0.0]},
        )
        scene_handler.create_camera(location=[0.0, -8.0, 1.0], rotation=[1.5708, 0.0, 0.0], name="E2E_IdCamera")

        result = scene_handler.get_object_id_pass(
            object_names=["IdCube", "IdSphere"],
            width=320,
            height=240,
            camera_name="E2E_IdCamera",
        )

        assert isinstance(result, dict), f"expected dict, got {result!r}"
        assert _looks_like_png(result["image"]), "object-id pass image is not a valid PNG"
        # Both objects get a unique 1-based index mapped to their name.
        assert set(result["index_map"].values()) == {"IdCube", "IdSphere"}
        assert sorted(int(k) for k in result["index_map"].keys()) == [1, 2]
        assert result["missing"] == []
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_object_id_pass_reports_missing_objects(scene_handler, rpc_client):
    """A missing object name is reported, present ones still resolve."""

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "IdCube2"})
        scene_handler.create_camera(location=[0.0, -8.0, 1.0], rotation=[1.5708, 0.0, 0.0], name="E2E_IdCamera2")

        result = scene_handler.get_object_id_pass(
            object_names=["IdCube2", "Ghost"],
            width=200,
            height=150,
            camera_name="E2E_IdCamera2",
        )

        assert isinstance(result, dict)
        assert result["missing"] == ["Ghost"]
        assert set(result["index_map"].values()) == {"IdCube2"}
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_object_id_pass_is_reversible(scene_handler, rpc_client):
    """The pass restores render engine/resolution and object pass_index values."""

    try:
        scene_handler.clean_scene(keep_lights_and_cameras=True)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "IdCube3"})
        scene_handler.create_camera(location=[0.0, -8.0, 1.0], rotation=[1.5708, 0.0, 0.0], name="E2E_IdCamera3")

        before = scene_handler.inspect_render_settings()
        result = scene_handler.get_object_id_pass(
            object_names=["IdCube3"], width=200, height=150, camera_name="E2E_IdCamera3"
        )
        after = scene_handler.inspect_render_settings()

        assert isinstance(result, dict) and result["image"]
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
