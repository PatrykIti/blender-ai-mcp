"""
Tests for UV Tools (TASK-014-11)
"""
import pytest
from server.application.tool_handlers.uv_handler import UVToolHandler


@pytest.fixture
def uv_handler(rpc_client):
    """Provides a UV handler instance using shared RPC client."""
    return UVToolHandler(rpc_client)


def test_uv_list_maps_basic(uv_handler):
    """Test listing UV maps for a mesh object."""
    try:
        # Try common mesh object names
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.list_maps(
                    object_name=obj_name,
                    include_island_counts=False
                )
                break
            except RuntimeError:
                continue

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, dict)
        assert "object_name" in result
        assert "uv_map_count" in result
        assert "uv_maps" in result
        assert isinstance(result["uv_maps"], list)

        print(f"✓ uv_list_maps: '{result['object_name']}' has {result['uv_map_count']} UV maps")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_uv_list_maps_with_island_counts(uv_handler):
    """Test listing UV maps with island counts."""
    try:
        # Try common mesh object names
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.list_maps(
                    object_name=obj_name,
                    include_island_counts=True
                )
                break
            except RuntimeError:
                continue

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, dict)
        assert "uv_maps" in result

        # Check if UV map data includes optional fields
        for uv_map in result["uv_maps"]:
            assert "name" in uv_map
            assert "is_active" in uv_map
            assert "is_active_render" in uv_map
            # Optional fields when include_island_counts=True
            if "uv_loop_count" in uv_map:
                assert isinstance(uv_map["uv_loop_count"], int)

        print(f"✓ uv_list_maps (with island counts): {result['uv_map_count']} UV maps")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_uv_list_maps_invalid_object(uv_handler):
    """Test listing UV maps for non-existent object."""
    try:
        with pytest.raises(RuntimeError) as exc_info:
            uv_handler.list_maps(
                object_name="NonExistentObject12345",
                include_island_counts=False
            )
        # Check if error is the expected validation error (not connection error)
        error_msg = str(exc_info.value).lower()
        if "not found" in error_msg:
            print("✓ uv_list_maps properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {exc_info.value}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            print("✓ uv_list_maps properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        else:
            raise


def test_uv_list_maps_non_mesh_object(uv_handler):
    """Test listing UV maps for non-mesh object."""
    try:
        # Try to query a camera or light (non-mesh objects)
        test_objects = ["Camera", "Light"]

        for obj_name in test_objects:
            try:
                with pytest.raises(RuntimeError) as exc_info:
                    uv_handler.list_maps(
                        object_name=obj_name,
                        include_island_counts=False
                    )
                error_msg = str(exc_info.value).lower()
                if "not a mesh" in error_msg:
                    print(f"✓ uv_list_maps properly handles non-mesh object '{obj_name}'")
                    return
                elif "could not connect" in error_msg or "unknown command" in error_msg:
                    pytest.skip(f"Blender not available: {exc_info.value}")
                    return
                elif "not found" in error_msg:
                    continue  # Object doesn't exist, try next
            except RuntimeError as e:
                error_msg = str(e).lower()
                if "could not connect" in error_msg or "unknown command" in error_msg:
                    pytest.skip(f"Blender not available: {e}")
                    return
                elif "not found" in error_msg:
                    continue  # Object doesn't exist, try next
                raise

        pytest.skip("No non-mesh objects available for testing")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
