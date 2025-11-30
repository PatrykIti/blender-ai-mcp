"""
E2E Tests for Lattice Deformation Tools (TASK-033)

Tests the complete workflow:
1. Create cube → create fitted lattice → bind → edit points → verify deformation
2. Taper workflow (tower example)
3. Vertex group binding
"""
import pytest
import time
from server.application.tool_handlers.lattice_handler import LatticeToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def lattice_handler(rpc_client):
    """Provides a lattice handler instance using shared RPC client."""
    return LatticeToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


# ============================================================================
# TASK-033-1: lattice_create Tests
# ============================================================================


def test_lattice_create_default(lattice_handler, scene_handler):
    """Test creating lattice with default parameters."""
    try:
        lattice_name = f"TestLattice_{int(time.time())}"

        result = lattice_handler.lattice_create(
            name=lattice_name,
            location=[0, 0, 0],
        )

        assert "Created lattice" in result
        assert lattice_name in result
        assert "2x2x2" in result  # Default resolution
        print(f"✓ lattice_create default: {result}")

        # Cleanup
        scene_handler.delete_object(lattice_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_create_custom_resolution(lattice_handler, scene_handler):
    """Test creating lattice with custom resolution."""
    try:
        lattice_name = f"HighResLattice_{int(time.time())}"

        result = lattice_handler.lattice_create(
            name=lattice_name,
            points_u=3,
            points_v=3,
            points_w=5,
            interpolation="KEY_BSPLINE",
        )

        assert "Created lattice" in result
        assert "3x3x5" in result
        assert "KEY_BSPLINE" in result
        print(f"✓ lattice_create custom resolution: {result}")

        # Cleanup
        scene_handler.delete_object(lattice_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_create_fitted_to_object(lattice_handler, modeling_handler, scene_handler):
    """Test creating lattice fitted to target object."""
    try:
        cube_name = f"TestCube_{int(time.time())}"
        lattice_name = f"FittedLattice_{int(time.time())}"

        # Create a cube first
        modeling_handler.create_primitive("Cube", name=cube_name, size=2.0)

        # Create lattice fitted to cube
        result = lattice_handler.lattice_create(
            name=lattice_name,
            target_object=cube_name,
            points_w=4,
        )

        assert "Created lattice" in result
        assert "fitted to" in result
        assert cube_name in result
        print(f"✓ lattice_create fitted: {result}")

        # Cleanup
        scene_handler.delete_object(lattice_name)
        scene_handler.delete_object(cube_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_create_invalid_target_object(lattice_handler):
    """Test error handling for non-existent target object."""
    try:
        lattice_handler.lattice_create(
            name="TestLattice",
            target_object="NonExistentObject12345",
        )
        assert False, "Expected RuntimeError for non-existent target"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ lattice_create properly handles non-existent target")
        else:
            raise


# ============================================================================
# TASK-033-2: lattice_bind Tests
# ============================================================================


def test_lattice_bind_basic(lattice_handler, modeling_handler, scene_handler):
    """Test binding object to lattice."""
    try:
        cube_name = f"TestCube_{int(time.time())}"
        lattice_name = f"TestLattice_{int(time.time())}"

        # Create cube
        modeling_handler.create_primitive("Cube", name=cube_name)

        # Create lattice
        lattice_handler.lattice_create(
            name=lattice_name,
            target_object=cube_name,
        )

        # Bind cube to lattice
        result = lattice_handler.lattice_bind(
            object_name=cube_name,
            lattice_name=lattice_name,
        )

        assert "Bound" in result
        assert cube_name in result
        assert lattice_name in result
        print(f"✓ lattice_bind basic: {result}")

        # Cleanup
        scene_handler.delete_object(lattice_name)
        scene_handler.delete_object(cube_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_bind_invalid_object(lattice_handler, scene_handler):
    """Test error handling for non-existent object."""
    try:
        lattice_name = f"TestLattice_{int(time.time())}"

        # Create lattice
        lattice_handler.lattice_create(name=lattice_name)

        try:
            lattice_handler.lattice_bind(
                object_name="NonExistentObject12345",
                lattice_name=lattice_name,
            )
            assert False, "Expected RuntimeError for non-existent object"
        except RuntimeError as e:
            if "not found" in str(e).lower():
                print("✓ lattice_bind properly handles non-existent object")
            else:
                raise

        # Cleanup
        scene_handler.delete_object(lattice_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_bind_invalid_lattice(lattice_handler, modeling_handler, scene_handler):
    """Test error handling for non-existent lattice."""
    try:
        cube_name = f"TestCube_{int(time.time())}"

        # Create cube
        modeling_handler.create_primitive("Cube", name=cube_name)

        try:
            lattice_handler.lattice_bind(
                object_name=cube_name,
                lattice_name="NonExistentLattice12345",
            )
            assert False, "Expected RuntimeError for non-existent lattice"
        except RuntimeError as e:
            if "not found" in str(e).lower():
                print("✓ lattice_bind properly handles non-existent lattice")
            else:
                raise

        # Cleanup
        scene_handler.delete_object(cube_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ============================================================================
# TASK-033-3: lattice_edit_point Tests
# ============================================================================


def test_lattice_edit_point_single(lattice_handler, scene_handler):
    """Test moving a single lattice point."""
    try:
        lattice_name = f"TestLattice_{int(time.time())}"

        # Create lattice with 8 points (2x2x2)
        lattice_handler.lattice_create(name=lattice_name)

        # Move point 0
        result = lattice_handler.lattice_edit_point(
            lattice_name=lattice_name,
            point_index=0,
            offset=[0.5, 0.5, 0],
            relative=True,
        )

        assert "Moved 1 point" in result
        print(f"✓ lattice_edit_point single: {result}")

        # Cleanup
        scene_handler.delete_object(lattice_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_edit_point_multiple(lattice_handler, scene_handler):
    """Test moving multiple lattice points."""
    try:
        lattice_name = f"TestLattice_{int(time.time())}"

        # Create lattice with 16 points (2x2x4)
        lattice_handler.lattice_create(
            name=lattice_name,
            points_w=4,
        )

        # Move top 4 points (indices 12-15) inward
        result = lattice_handler.lattice_edit_point(
            lattice_name=lattice_name,
            point_index=[12, 13, 14, 15],
            offset=[-0.3, -0.3, 0],
            relative=True,
        )

        assert "Moved 4 point" in result
        print(f"✓ lattice_edit_point multiple: {result}")

        # Cleanup
        scene_handler.delete_object(lattice_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_edit_point_absolute(lattice_handler, scene_handler):
    """Test setting point to absolute position."""
    try:
        lattice_name = f"TestLattice_{int(time.time())}"

        # Create lattice
        lattice_handler.lattice_create(name=lattice_name)

        # Set point to absolute position
        result = lattice_handler.lattice_edit_point(
            lattice_name=lattice_name,
            point_index=7,
            offset=[0.5, 0.5, 0.5],
            relative=False,
        )

        assert "Set 1 point" in result
        print(f"✓ lattice_edit_point absolute: {result}")

        # Cleanup
        scene_handler.delete_object(lattice_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_edit_point_invalid_index(lattice_handler, scene_handler):
    """Test error handling for invalid point index."""
    try:
        lattice_name = f"TestLattice_{int(time.time())}"

        # Create lattice with 8 points (2x2x2)
        lattice_handler.lattice_create(name=lattice_name)

        try:
            lattice_handler.lattice_edit_point(
                lattice_name=lattice_name,
                point_index=100,  # Out of range
                offset=[0, 0, 1],
            )
            assert False, "Expected RuntimeError for invalid index"
        except RuntimeError as e:
            if "out of range" in str(e).lower():
                print("✓ lattice_edit_point properly handles invalid index")
            else:
                raise

        # Cleanup
        scene_handler.delete_object(lattice_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ============================================================================
# Complete Workflow Tests
# ============================================================================


def test_complete_taper_workflow(lattice_handler, modeling_handler, scene_handler):
    """Test the complete Eiffel Tower tapering workflow from TASK-033 specification."""
    try:
        tower_name = f"Tower_{int(time.time())}"
        lattice_name = f"TowerLattice_{int(time.time())}"

        # 1. Create tower base (tall cube)
        modeling_handler.create_primitive("Cube", name=tower_name)
        modeling_handler.transform_object(tower_name, scale=[0.5, 0.5, 3.0])

        # 2. Create lattice fitted to tower with 4 vertical divisions
        result1 = lattice_handler.lattice_create(
            name=lattice_name,
            target_object=tower_name,
            points_u=2,
            points_v=2,
            points_w=4,
        )
        assert "Created lattice" in result1
        assert "fitted to" in result1

        # 3. Bind tower to lattice
        result2 = lattice_handler.lattice_bind(
            object_name=tower_name,
            lattice_name=lattice_name,
        )
        assert "Bound" in result2

        # 4. Taper by moving top points inward
        # For 2x2x4 = 16 points, top layer is indices 12-15
        result3 = lattice_handler.lattice_edit_point(
            lattice_name=lattice_name,
            point_index=[12, 13, 14, 15],
            offset=[-0.3, -0.3, 0],
            relative=True,
        )
        assert "Moved 4 point" in result3

        print("✓ Complete taper workflow successful:")
        print(f"  - Created tower: {tower_name}")
        print(f"  - Created and fitted lattice: {lattice_name}")
        print(f"  - Bound and deformed: tapered top points")

        # Cleanup
        scene_handler.delete_object(lattice_name)
        scene_handler.delete_object(tower_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_lattice_deformation_multiple_objects(lattice_handler, modeling_handler, scene_handler):
    """Test binding multiple objects to the same lattice."""
    try:
        cube1_name = f"Cube1_{int(time.time())}"
        cube2_name = f"Cube2_{int(time.time())}"
        lattice_name = f"SharedLattice_{int(time.time())}"

        # Create two cubes side by side
        modeling_handler.create_primitive("Cube", name=cube1_name, location=[-1.5, 0, 0])
        modeling_handler.create_primitive("Cube", name=cube2_name, location=[1.5, 0, 0])

        # Create large lattice covering both
        lattice_handler.lattice_create(
            name=lattice_name,
            location=[0, 0, 0],
            points_u=4,
            points_v=2,
            points_w=2,
        )

        # Bind both cubes to lattice
        result1 = lattice_handler.lattice_bind(
            object_name=cube1_name,
            lattice_name=lattice_name,
        )
        result2 = lattice_handler.lattice_bind(
            object_name=cube2_name,
            lattice_name=lattice_name,
        )

        assert "Bound" in result1
        assert "Bound" in result2
        print("✓ Multiple objects bound to same lattice successfully")

        # Cleanup
        scene_handler.delete_object(lattice_name)
        scene_handler.delete_object(cube1_name)
        scene_handler.delete_object(cube2_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
