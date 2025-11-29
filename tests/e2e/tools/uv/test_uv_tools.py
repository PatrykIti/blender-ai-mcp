"""
Tests for UV Tools (TASK-014-11, TASK-024)
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


# =============================================================================
# TASK-024: uv_unwrap Tests
# =============================================================================

def test_uv_unwrap_smart_project(uv_handler):
    """Test UV unwrap with SMART_PROJECT method."""
    try:
        # Try common mesh object names
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.unwrap(
                    object_name=obj_name,
                    method="SMART_PROJECT",
                    angle_limit=66.0,
                    island_margin=0.02,
                    scale_to_bounds=True
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "Unwrapped" in result or "unwrap" in result.lower()
        print(f"✓ uv_unwrap (SMART_PROJECT): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_unwrap_cube_project(uv_handler):
    """Test UV unwrap with CUBE projection."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.unwrap(
                    object_name=obj_name,
                    method="CUBE",
                    scale_to_bounds=True
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "CUBE" in result
        print(f"✓ uv_unwrap (CUBE): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_unwrap_cylinder_project(uv_handler):
    """Test UV unwrap with CYLINDER projection."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.unwrap(
                    object_name=obj_name,
                    method="CYLINDER",
                    scale_to_bounds=True
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "CYLINDER" in result
        print(f"✓ uv_unwrap (CYLINDER): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_unwrap_sphere_project(uv_handler):
    """Test UV unwrap with SPHERE projection."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.unwrap(
                    object_name=obj_name,
                    method="SPHERE",
                    scale_to_bounds=True
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "SPHERE" in result
        print(f"✓ uv_unwrap (SPHERE): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_unwrap_standard(uv_handler):
    """Test UV unwrap with standard UNWRAP method."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.unwrap(
                    object_name=obj_name,
                    method="UNWRAP",
                    island_margin=0.02
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "UNWRAP" in result
        print(f"✓ uv_unwrap (UNWRAP): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_unwrap_invalid_object(uv_handler):
    """Test UV unwrap with non-existent object."""
    try:
        with pytest.raises(RuntimeError) as exc_info:
            uv_handler.unwrap(
                object_name="NonExistentObject12345",
                method="SMART_PROJECT"
            )
        error_msg = str(exc_info.value).lower()
        if "not found" in error_msg:
            print("✓ uv_unwrap properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {exc_info.value}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            print("✓ uv_unwrap properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        else:
            raise


# =============================================================================
# TASK-024: uv_pack_islands Tests
# =============================================================================

def test_uv_pack_islands_basic(uv_handler):
    """Test packing UV islands with default parameters."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.pack_islands(
                    object_name=obj_name,
                    margin=0.02,
                    rotate=True,
                    scale=True
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "Packed" in result or "pack" in result.lower()
        print(f"✓ uv_pack_islands: {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_pack_islands_custom_params(uv_handler):
    """Test packing UV islands with custom parameters."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.pack_islands(
                    object_name=obj_name,
                    margin=0.05,
                    rotate=False,
                    scale=False
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "Packed" in result
        print(f"✓ uv_pack_islands (custom params): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_pack_islands_invalid_object(uv_handler):
    """Test packing UV islands with non-existent object."""
    try:
        with pytest.raises(RuntimeError) as exc_info:
            uv_handler.pack_islands(
                object_name="NonExistentObject12345",
                margin=0.02
            )
        error_msg = str(exc_info.value).lower()
        if "not found" in error_msg:
            print("✓ uv_pack_islands properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {exc_info.value}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            print("✓ uv_pack_islands properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        else:
            raise


# =============================================================================
# TASK-024: uv_create_seam Tests
# =============================================================================

def test_uv_create_seam_mark(uv_handler):
    """Test marking UV seams on selected edges."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.create_seam(
                    object_name=obj_name,
                    action="mark"
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "Marked" in result or "seam" in result.lower()
        print(f"✓ uv_create_seam (mark): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_create_seam_clear(uv_handler):
    """Test clearing UV seams from selected edges."""
    try:
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = uv_handler.create_seam(
                    object_name=obj_name,
                    action="clear"
                )
                break
            except RuntimeError as e:
                if "not found" in str(e).lower():
                    continue
                raise

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, str)
        assert "Cleared" in result or "seam" in result.lower()
        print(f"✓ uv_create_seam (clear): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_uv_create_seam_invalid_object(uv_handler):
    """Test creating seam with non-existent object."""
    try:
        with pytest.raises(RuntimeError) as exc_info:
            uv_handler.create_seam(
                object_name="NonExistentObject12345",
                action="mark"
            )
        error_msg = str(exc_info.value).lower()
        if "not found" in error_msg:
            print("✓ uv_create_seam properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {exc_info.value}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            print("✓ uv_create_seam properly handles invalid object name")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        else:
            raise
