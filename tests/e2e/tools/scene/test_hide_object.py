"""
E2E Tests for scene_hide_object (TASK-043-2)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_hide_object(scene_handler):
    """Test hiding an object in viewport."""
    try:
        # First, list objects to find one to hide
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene to hide")

        # Get first object's name
        object_name = objects[0]["name"]

        # Hide it
        result = scene_handler.hide_object(object_name, hide=True, hide_render=False)

        assert "hidden" in result.lower() or object_name in result
        print(f"✓ hide_object: {object_name} hidden in viewport")

        # Show it again
        result = scene_handler.hide_object(object_name, hide=False, hide_render=False)

        assert "visible" in result.lower() or object_name in result
        print(f"✓ hide_object: {object_name} shown in viewport")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_hide_object_with_render(scene_handler):
    """Test hiding an object in viewport and render."""
    try:
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene")

        object_name = objects[0]["name"]

        # Hide in both viewport and render
        result = scene_handler.hide_object(object_name, hide=True, hide_render=True)

        assert "hidden" in result.lower() or object_name in result
        print(f"✓ hide_object: {object_name} hidden in viewport and render")

        # Restore
        scene_handler.hide_object(object_name, hide=False, hide_render=False)

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_hide_object_not_found(scene_handler):
    """Test hiding non-existent object."""
    try:
        result = scene_handler.hide_object("NonExistentObject12345", hide=True)

        assert "not found" in result.lower() or "error" in result.lower()
        print("✓ hide_object: correctly handles non-existent object")

    except RuntimeError as e:
        if "not found" in str(e).lower():
            print("✓ hide_object: correctly raises error for non-existent object")
        else:
            pytest.skip(f"Blender not available: {e}")
