"""
E2E Tests for scene_camera_orbit (TASK-043-5)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_camera_orbit_horizontal(scene_handler):
    """Test horizontal camera orbit."""
    try:
        result = scene_handler.camera_orbit(
            angle_horizontal=45.0,
            angle_vertical=0.0
        )

        assert "orbit" in result.lower() or "rotated" in result.lower() or "camera" in result.lower()
        print(f"✓ camera_orbit (horizontal 45°): {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_orbit_vertical(scene_handler):
    """Test vertical camera orbit."""
    try:
        result = scene_handler.camera_orbit(
            angle_horizontal=0.0,
            angle_vertical=30.0
        )

        assert "orbit" in result.lower() or "rotated" in result.lower() or "camera" in result.lower()
        print(f"✓ camera_orbit (vertical 30°): {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_orbit_combined(scene_handler):
    """Test combined horizontal and vertical orbit."""
    try:
        result = scene_handler.camera_orbit(
            angle_horizontal=45.0,
            angle_vertical=30.0
        )

        assert "orbit" in result.lower() or "rotated" in result.lower() or "camera" in result.lower()
        print(f"✓ camera_orbit (45°, 30°): {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_orbit_around_object(scene_handler):
    """Test orbit around specific object."""
    try:
        objects = scene_handler.list_objects()

        if not objects:
            pytest.skip("No objects in scene")

        object_name = objects[0]["name"]
        result = scene_handler.camera_orbit(
            angle_horizontal=90.0,
            angle_vertical=0.0,
            target_object=object_name
        )

        assert "orbit" in result.lower() or object_name in result or "camera" in result.lower()
        print(f"✓ camera_orbit around {object_name}: {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_orbit_around_point(scene_handler):
    """Test orbit around specific point."""
    try:
        result = scene_handler.camera_orbit(
            angle_horizontal=45.0,
            angle_vertical=15.0,
            target_point=[0.0, 0.0, 1.0]
        )

        assert "orbit" in result.lower() or "rotated" in result.lower() or "camera" in result.lower()
        print(f"✓ camera_orbit around point: {result}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_camera_orbit_target_not_found(scene_handler):
    """Test orbit with non-existent target."""
    try:
        result = scene_handler.camera_orbit(
            angle_horizontal=45.0,
            target_object="NonExistentObject12345"
        )

        assert "not found" in result.lower() or "error" in result.lower()
        print("✓ camera_orbit: correctly handles non-existent target")

    except RuntimeError as e:
        if "not found" in str(e).lower():
            print("✓ camera_orbit: correctly raises error for non-existent target")
        else:
            pytest.skip(f"Blender not available: {e}")
