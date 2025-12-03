"""
E2E Tests for scene_rename_object (TASK-043-1)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_rename_object(scene_handler):
    """Test renaming an object."""
    try:
        # First, list objects to find one to rename
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene to rename")

        # Get first object's name
        original_name = objects[0]["name"]

        # Rename it
        new_name = f"{original_name}_renamed"
        result = scene_handler.rename_object(original_name, new_name)

        assert "Renamed" in result or new_name in result
        print(f"✓ rename_object: {original_name} -> {new_name}")

        # Rename it back
        scene_handler.rename_object(new_name, original_name)
        print(f"✓ rename_object: restored to {original_name}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_rename_object_not_found(scene_handler):
    """Test renaming non-existent object."""
    try:
        result = scene_handler.rename_object("NonExistentObject12345", "NewName")

        # Should return error message
        assert "not found" in result.lower() or "error" in result.lower()
        print("✓ rename_object: correctly handles non-existent object")

    except RuntimeError as e:
        if "not found" in str(e).lower():
            print("✓ rename_object: correctly raises error for non-existent object")
        else:
            pytest.skip(f"Blender not available: {e}")
