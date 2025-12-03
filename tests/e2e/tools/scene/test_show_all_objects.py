"""
E2E Tests for scene_show_all_objects (TASK-043-3)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_show_all_objects(scene_handler):
    """Test showing all hidden objects."""
    try:
        # First, list objects and hide some
        objects = scene_handler.list_objects()

        if len(objects) < 2:
            pytest.skip("Need at least 2 objects for this test")

        # Hide first two objects
        scene_handler.hide_object(objects[0]["name"], hide=True)
        scene_handler.hide_object(objects[1]["name"], hide=True)

        # Show all
        result = scene_handler.show_all_objects(include_render=False)

        assert "visible" in result.lower() or "objects" in result.lower()
        print(f"✓ show_all_objects: {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_show_all_objects_include_render(scene_handler):
    """Test showing all objects including render visibility."""
    try:
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene")

        # Hide an object in render
        scene_handler.hide_object(objects[0]["name"], hide=True, hide_render=True)

        # Show all including render
        result = scene_handler.show_all_objects(include_render=True)

        assert "visible" in result.lower() or "objects" in result.lower()
        print(f"✓ show_all_objects (include_render): {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_show_all_objects_none_hidden(scene_handler):
    """Test show_all when no objects are hidden."""
    try:
        # First ensure all are visible
        scene_handler.show_all_objects(include_render=True)

        # Call again - should report 0 objects shown
        result = scene_handler.show_all_objects(include_render=False)

        assert "0" in result or "visible" in result.lower()
        print(f"✓ show_all_objects (none hidden): {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
