"""
Tests for UV Tools (TASK-014-11, TASK-024)
"""
import pytest
from server.application.tool_handlers.uv_handler import UVToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def uv_handler(rpc_client):
    """Provides a UV handler instance using shared RPC client."""
    return UVToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def create_test_object(modeling_handler, scene_handler, name="E2E_UVTest"):
    """Helper to create a test cube for UV operations."""
    # Clean up if exists
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass

    # Create cube
    modeling_handler.create_primitive(
        primitive_type="CUBE",
        name=name,
        location=[0, 0, 0]
    )
    return name


def cleanup_test_object(scene_handler, name):
    """Helper to clean up test object."""
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass


# =============================================================================
# UV List Maps Tests
# =============================================================================

def test_uv_list_maps_basic(uv_handler, modeling_handler, scene_handler):
    """Test listing UV maps for a mesh object."""
    obj_name = "E2E_UVListTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.list_maps(
            object_name=obj_name,
            include_island_counts=False
        )

        assert isinstance(result, dict)
        assert "object_name" in result
        assert "uv_map_count" in result
        assert "uv_maps" in result
        assert isinstance(result["uv_maps"], list)

        print(f"✓ uv_list_maps: '{result['object_name']}' has {result['uv_map_count']} UV maps")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


def test_uv_list_maps_with_island_counts(uv_handler, modeling_handler, scene_handler):
    """Test listing UV maps with island counts."""
    obj_name = "E2E_UVListIslandsTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.list_maps(
            object_name=obj_name,
            include_island_counts=True
        )

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
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


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


def test_uv_list_maps_non_mesh_object(uv_handler, scene_handler):
    """Test listing UV maps for non-mesh object."""
    try:
        # Create a camera (non-mesh object)
        camera_name = "E2E_UVTestCamera"
        try:
            scene_handler.create_camera(
                location=[0, 0, 5],
                rotation=[0, 0, 0],
                name=camera_name
            )
        except RuntimeError as e:
            if "could not connect" in str(e).lower():
                pytest.skip(f"Blender not available: {e}")
            raise

        with pytest.raises(RuntimeError) as exc_info:
            uv_handler.list_maps(
                object_name=camera_name,
                include_island_counts=False
            )
        error_msg = str(exc_info.value).lower()
        if "not a mesh" in error_msg:
            print(f"✓ uv_list_maps properly handles non-mesh object '{camera_name}'")
        elif "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {exc_info.value}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, "E2E_UVTestCamera")


# =============================================================================
# TASK-024: uv_unwrap Tests
# =============================================================================

def test_uv_unwrap_smart_project(uv_handler, modeling_handler, scene_handler):
    """Test UV unwrap with SMART_PROJECT method."""
    obj_name = "E2E_UVUnwrapSmartTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.unwrap(
            object_name=obj_name,
            method="SMART_PROJECT",
            angle_limit=66.0,
            island_margin=0.02,
            scale_to_bounds=True
        )

        assert isinstance(result, str)
        assert "Unwrapped" in result or "unwrap" in result.lower()
        print(f"✓ uv_unwrap (SMART_PROJECT): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


def test_uv_unwrap_cube_project(uv_handler, modeling_handler, scene_handler):
    """Test UV unwrap with CUBE projection."""
    obj_name = "E2E_UVUnwrapCubeTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.unwrap(
            object_name=obj_name,
            method="CUBE",
            scale_to_bounds=True
        )

        assert isinstance(result, str)
        assert "CUBE" in result
        print(f"✓ uv_unwrap (CUBE): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


def test_uv_unwrap_cylinder_project(uv_handler, modeling_handler, scene_handler):
    """Test UV unwrap with CYLINDER projection."""
    obj_name = "E2E_UVUnwrapCylTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.unwrap(
            object_name=obj_name,
            method="CYLINDER",
            scale_to_bounds=True
        )

        assert isinstance(result, str)
        assert "CYLINDER" in result
        print(f"✓ uv_unwrap (CYLINDER): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


def test_uv_unwrap_sphere_project(uv_handler, modeling_handler, scene_handler):
    """Test UV unwrap with SPHERE projection."""
    obj_name = "E2E_UVUnwrapSphereTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.unwrap(
            object_name=obj_name,
            method="SPHERE",
            scale_to_bounds=True
        )

        assert isinstance(result, str)
        assert "SPHERE" in result
        print(f"✓ uv_unwrap (SPHERE): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


def test_uv_unwrap_standard(uv_handler, modeling_handler, scene_handler):
    """Test UV unwrap with standard UNWRAP method."""
    obj_name = "E2E_UVUnwrapStdTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.unwrap(
            object_name=obj_name,
            method="UNWRAP",
            island_margin=0.02
        )

        assert isinstance(result, str)
        assert "UNWRAP" in result
        print(f"✓ uv_unwrap (UNWRAP): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


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

def test_uv_pack_islands_basic(uv_handler, modeling_handler, scene_handler):
    """Test packing UV islands with default parameters."""
    obj_name = "E2E_UVPackTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.pack_islands(
            object_name=obj_name,
            margin=0.02,
            rotate=True,
            scale=True
        )

        assert isinstance(result, str)
        assert "Packed" in result or "pack" in result.lower()
        print(f"✓ uv_pack_islands: {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


def test_uv_pack_islands_custom_params(uv_handler, modeling_handler, scene_handler):
    """Test packing UV islands with custom parameters."""
    obj_name = "E2E_UVPackCustomTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.pack_islands(
            object_name=obj_name,
            margin=0.05,
            rotate=False,
            scale=False
        )

        assert isinstance(result, str)
        assert "Packed" in result
        print(f"✓ uv_pack_islands (custom params): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


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

def test_uv_create_seam_mark(uv_handler, modeling_handler, scene_handler):
    """Test marking UV seams on selected edges."""
    obj_name = "E2E_UVSeamMarkTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.create_seam(
            object_name=obj_name,
            action="mark"
        )

        assert isinstance(result, str)
        assert "Marked" in result or "seam" in result.lower()
        print(f"✓ uv_create_seam (mark): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


def test_uv_create_seam_clear(uv_handler, modeling_handler, scene_handler):
    """Test clearing UV seams from selected edges."""
    obj_name = "E2E_UVSeamClearTest"
    try:
        create_test_object(modeling_handler, scene_handler, obj_name)

        result = uv_handler.create_seam(
            object_name=obj_name,
            action="clear"
        )

        assert isinstance(result, str)
        assert "Cleared" in result or "seam" in result.lower()
        print(f"✓ uv_create_seam (clear): {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "unknown command" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        cleanup_test_object(scene_handler, obj_name)


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
