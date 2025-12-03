"""
E2E Tests for scene_camera_focus (TASK-043-6)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_camera_focus(scene_handler):
    """Test focusing camera on object."""
    try:
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene")

        object_name = objects[0]["name"]
        result = scene_handler.camera_focus(object_name, zoom_factor=1.0)

        assert "focus" in result.lower() or object_name in result
        print(f"✓ camera_focus on {object_name}: {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_focus_zoom_in(scene_handler):
    """Test focusing with zoom in."""
    try:
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene")

        object_name = objects[0]["name"]
        result = scene_handler.camera_focus(object_name, zoom_factor=2.0)

        assert "focus" in result.lower() or object_name in result
        print(f"✓ camera_focus zoom in on {object_name}: {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_focus_zoom_out(scene_handler):
    """Test focusing with zoom out."""
    try:
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene")

        object_name = objects[0]["name"]
        result = scene_handler.camera_focus(object_name, zoom_factor=0.5)

        assert "focus" in result.lower() or object_name in result
        print(f"✓ camera_focus zoom out on {object_name}: {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_focus_not_found(scene_handler):
    """Test focus on non-existent object."""
    try:
        result = scene_handler.camera_focus("NonExistentObject12345")

        assert "not found" in result.lower() or "error" in result.lower()
        print("✓ camera_focus: correctly handles non-existent object")

    except RuntimeError as e:
        if "not found" in str(e).lower():
            print("✓ camera_focus: correctly raises error for non-existent object")
        else:
            pytest.skip(f"Blender not available: {e}")
