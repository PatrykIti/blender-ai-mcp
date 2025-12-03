"""
E2E Tests for scene_isolate_object (TASK-043-4)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_isolate_single_object(scene_handler):
    """Test isolating a single object."""
    try:
        objects = scene_handler.list_objects()

        if len(objects) < 2:
            pytest.skip("Need at least 2 objects for isolation test")

        # Isolate first object
        object_name = objects[0]["name"]
        result = scene_handler.isolate_object([object_name])

        assert "Isolated" in result or "hid" in result.lower()
        print(f"✓ isolate_object: isolated {object_name}")

        # Restore all
        scene_handler.show_all_objects()

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_isolate_multiple_objects(scene_handler):
    """Test isolating multiple objects."""
    try:
        objects = scene_handler.list_objects()

        if len(objects) < 3:
            pytest.skip("Need at least 3 objects for this test")

        # Isolate first two objects
        names = [objects[0]["name"], objects[1]["name"]]
        result = scene_handler.isolate_object(names)

        assert "Isolated" in result or "hid" in result.lower()
        print(f"✓ isolate_object: isolated {names}")

        # Restore all
        scene_handler.show_all_objects()

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_isolate_and_show_all_workflow(scene_handler):
    """Test isolate → show_all workflow."""
    try:
        objects = scene_handler.list_objects()

        if len(objects) < 2:
            pytest.skip("Need at least 2 objects")

        # Isolate
        scene_handler.isolate_object([objects[0]["name"]])

        # Show all
        result = scene_handler.show_all_objects()

        # Should have made some objects visible again
        assert "visible" in result.lower() or "objects" in result.lower()
        print(f"✓ isolate → show_all workflow: {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
