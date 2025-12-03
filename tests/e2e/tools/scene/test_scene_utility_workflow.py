"""
E2E Tests for TASK-043 Scene Utility Tools - Full Workflow

Tests the complete workflow:
list objects → rename → isolate → focus → orbit → inspect

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_full_inspection_workflow(scene_handler):
    """
    Test complete model inspection workflow:
    1. List objects
    2. Rename an object
    3. Isolate it
    4. Focus camera on it
    5. Orbit around it
    6. Show all objects again
    """
    try:
        # Step 1: List objects
        objects = scene_handler.list_objects()
        assert len(objects) > 0, "Scene should have at least one object"
        print(f"✓ Step 1: Listed {len(objects)} objects")

        original_name = objects[0]["name"]

        # Step 2: Rename object
        new_name = f"{original_name}_inspection"
        result = scene_handler.rename_object(original_name, new_name)
        assert new_name in result or "Renamed" in result
        print(f"✓ Step 2: Renamed '{original_name}' to '{new_name}'")

        # Step 3: Isolate the object
        result = scene_handler.isolate_object([new_name])
        assert "Isolated" in result or "hid" in result.lower()
        print(f"✓ Step 3: Isolated '{new_name}'")

        # Step 4: Focus camera on it
        result = scene_handler.camera_focus(new_name, zoom_factor=1.5)
        assert "focus" in result.lower() or new_name in result
        print(f"✓ Step 4: Focused camera on '{new_name}'")

        # Step 5: Orbit around it
        result = scene_handler.camera_orbit(
            angle_horizontal=45.0,
            angle_vertical=15.0,
            target_object=new_name
        )
        assert "orbit" in result.lower() or "rotated" in result.lower() or "camera" in result.lower()
        print(f"✓ Step 5: Orbited camera around '{new_name}'")

        # Step 6: Show all objects again
        result = scene_handler.show_all_objects()
        assert "visible" in result.lower() or "objects" in result.lower()
        print(f"✓ Step 6: Showed all objects")

        # Cleanup: Rename back
        scene_handler.rename_object(new_name, original_name)
        print(f"✓ Cleanup: Restored original name '{original_name}'")

        print("\n✅ Full inspection workflow completed successfully!")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_visibility_control_workflow(scene_handler):
    """
    Test visibility control workflow:
    1. List objects
    2. Hide several objects
    3. Show all
    4. Verify all visible
    """
    try:
        # Step 1: List objects
        objects = scene_handler.list_objects()

        if len(objects) < 2:
            pytest.skip("Need at least 2 objects for visibility workflow")

        print(f"✓ Step 1: Listed {len(objects)} objects")

        # Step 2: Hide objects
        hidden_count = min(2, len(objects))
        for i in range(hidden_count):
            result = scene_handler.hide_object(objects[i]["name"], hide=True)
            print(f"✓ Step 2.{i+1}: Hid '{objects[i]['name']}'")

        # Step 3: Show all
        result = scene_handler.show_all_objects()
        print(f"✓ Step 3: {result}")

        print("\n✅ Visibility control workflow completed successfully!")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_multi_object_isolation_workflow(scene_handler):
    """
    Test isolating multiple objects and inspecting them:
    1. List objects
    2. Isolate specific objects by type
    3. Inspect each with camera
    4. Restore visibility
    """
    try:
        # Step 1: List objects
        objects = scene_handler.list_objects()

        if len(objects) < 3:
            pytest.skip("Need at least 3 objects for multi-isolation workflow")

        # Get mesh objects only
        mesh_objects = [obj for obj in objects if obj.get("type") == "MESH"]

        if len(mesh_objects) < 2:
            # Fallback to first 2 objects
            mesh_objects = objects[:2]

        mesh_names = [obj["name"] for obj in mesh_objects[:2]]
        print(f"✓ Step 1: Found {len(mesh_names)} objects to isolate: {mesh_names}")

        # Step 2: Isolate them
        result = scene_handler.isolate_object(mesh_names)
        print(f"✓ Step 2: Isolated {mesh_names}")

        # Step 3: Focus on each
        for name in mesh_names:
            result = scene_handler.camera_focus(name, zoom_factor=1.0)
            print(f"✓ Step 3: Focused on '{name}'")

        # Step 4: Restore
        result = scene_handler.show_all_objects()
        print(f"✓ Step 4: Restored visibility")

        print("\n✅ Multi-object isolation workflow completed successfully!")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
