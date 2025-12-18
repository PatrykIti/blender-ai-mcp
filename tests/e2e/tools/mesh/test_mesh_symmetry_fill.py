"""
E2E Tests for TASK-036: Symmetry & Advanced Fill

Tests require a running Blender instance with the addon loaded.
Run: pytest tests/e2e/tools/mesh/test_mesh_symmetry_fill.py -v

Tested tools:
- mesh_symmetrize
- mesh_grid_fill
- mesh_poke_faces
- mesh_beautify_fill
- mesh_mirror
"""
import pytest
from server.application.tool_handlers.mesh_handler import MeshToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def mesh_handler(rpc_client):
    """Provides a mesh handler instance using shared RPC client."""
    return MeshToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


# ==============================================================================
# Setup Helpers
# ==============================================================================

def create_test_cube(modeling_handler, scene_handler, name="E2E_SymmetryFillCube"):
    """Creates a test cube for symmetry/fill operations."""
    try:
        # Clean up existing
        scene_handler.delete_object(name)
    except RuntimeError:
        pass  # Object didn't exist

    # Create cube
    modeling_handler.create_primitive(
        primitive_type="CUBE",
        size=2.0,
        location=[0, 0, 0],
        name=name
    )
    return name


def create_asymmetric_mesh(modeling_handler, scene_handler, mesh_handler, name="E2E_AsymmetricMesh"):
    """Creates an asymmetric mesh for symmetrize testing."""
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass

    # Create cube and make it asymmetric
    modeling_handler.create_primitive(
        primitive_type="CUBE",
        size=2.0,
        location=[0, 0, 0],
        name=name
    )

    # Enter edit mode and modify one side
    scene_handler.set_active_object(name)
    scene_handler.set_mode("EDIT")
    mesh_handler.select_all(deselect=True)

    # Select vertices on positive X side only
    mesh_handler.select_by_location(axis='X', min_coord=0.5, max_coord=2.0, mode='VERT')

    # Move them to make it asymmetric
    mesh_handler.transform_selected(translate=[0.5, 0, 0])

    scene_handler.set_mode("OBJECT")
    return name


def create_mesh_with_hole(modeling_handler, scene_handler, mesh_handler, name="E2E_MeshWithHole"):
    """Creates a mesh with a hole for grid fill testing."""
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass

    # Create plane
    modeling_handler.create_primitive(
        primitive_type="PLANE",
        size=2.0,
        location=[0, 0, 0],
        name=name
    )

    # Subdivide to get more geometry
    scene_handler.set_active_object(name)
    scene_handler.set_mode("EDIT")
    mesh_handler.select_all(deselect=False)
    mesh_handler.subdivide(number_cuts=2)

    # Delete center face to create hole
    mesh_handler.select_all(deselect=True)
    mesh_handler.select_by_location(axis='X', min_coord=-0.3, max_coord=0.3, mode='FACE')
    mesh_handler.select_by_location(axis='Y', min_coord=-0.3, max_coord=0.3, mode='FACE')

    # Delete the selected face
    mesh_handler.delete_selected(type='FACE')

    scene_handler.set_mode("OBJECT")
    return name


def create_triangulated_mesh(modeling_handler, scene_handler, mesh_handler, name="E2E_TriangulatedMesh"):
    """Creates a triangulated mesh for beautify fill testing."""
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass

    # Create sphere (has triangles)
    modeling_handler.create_primitive(
        primitive_type="SPHERE",
        radius=1.0,
        location=[0, 0, 0],
        name=name
    )

    # Triangulate to ensure we have triangles
    scene_handler.set_active_object(name)
    scene_handler.set_mode("EDIT")
    mesh_handler.select_all(deselect=False)
    mesh_handler.triangulate()
    scene_handler.set_mode("OBJECT")

    return name


def enter_edit_mode_and_select_all(scene_handler, mesh_handler, object_name):
    """Enters edit mode and selects all geometry."""
    scene_handler.set_active_object(object_name)
    scene_handler.set_mode("EDIT")
    mesh_handler.select_all(deselect=False)


# ==============================================================================
# TASK-036-1: mesh_symmetrize Tests
# ==============================================================================

def test_symmetrize_default(mesh_handler, modeling_handler, scene_handler):
    """Test symmetrize with default parameters (NEGATIVE_X)."""
    try:
        # Setup: Create asymmetric mesh
        obj_name = create_asymmetric_mesh(modeling_handler, scene_handler, mesh_handler, "E2E_Symmetrize1")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test symmetrize
        result = mesh_handler.symmetrize()

        # Verify
        assert "symmetrized" in result.lower()
        assert "NEGATIVE_X" in result
        print(f"✓ symmetrize (default): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_symmetrize_positive_x(mesh_handler, modeling_handler, scene_handler):
    """Test symmetrize with POSITIVE_X direction."""
    try:
        # Setup
        obj_name = create_asymmetric_mesh(modeling_handler, scene_handler, mesh_handler, "E2E_Symmetrize2")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test symmetrize POSITIVE_X
        result = mesh_handler.symmetrize(direction="POSITIVE_X")

        # Verify
        assert "symmetrized" in result.lower()
        assert "POSITIVE_X" in result
        print(f"✓ symmetrize (POSITIVE_X): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_symmetrize_y_axis(mesh_handler, modeling_handler, scene_handler):
    """Test symmetrize on Y axis."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Symmetrize3")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test symmetrize on Y
        result = mesh_handler.symmetrize(direction="NEGATIVE_Y")

        # Verify
        assert "symmetrized" in result.lower()
        assert "NEGATIVE_Y" in result
        print(f"✓ symmetrize (NEGATIVE_Y): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_symmetrize_custom_threshold(mesh_handler, modeling_handler, scene_handler):
    """Test symmetrize with custom threshold."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Symmetrize4")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test with custom threshold
        result = mesh_handler.symmetrize(threshold=0.01)

        # Verify
        assert "symmetrized" in result.lower()
        assert "0.01" in result
        print(f"✓ symmetrize (custom threshold): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_symmetrize_invalid_direction_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that invalid direction raises error."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Symmetrize5")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test - should raise error
        mesh_handler.symmetrize(direction="INVALID")
        assert False, "Expected error for invalid direction"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid direction" in error_msg:
            print("✓ symmetrize properly handles invalid direction")
        else:
            raise
    finally:
        try:
            scene_handler.set_mode("OBJECT")
        except RuntimeError:
            pass


# ==============================================================================
# TASK-036-2: mesh_grid_fill Tests
# ==============================================================================

def test_grid_fill_default(mesh_handler, modeling_handler, scene_handler):
    """Test grid fill with default parameters."""
    try:
        # Setup: Create mesh with hole
        obj_name = create_mesh_with_hole(modeling_handler, scene_handler, mesh_handler, "E2E_GridFill1")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Select boundary edges
        mesh_handler.select_all(deselect=True)
        mesh_handler.select_boundary(mode="EDGE")

        # Test grid fill
        result = mesh_handler.grid_fill()

        # Verify
        assert "grid filled" in result.lower()
        print(f"✓ grid_fill (default): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_grid_fill_custom_span(mesh_handler, modeling_handler, scene_handler):
    """Test grid fill with custom span."""
    try:
        # Setup
        obj_name = create_mesh_with_hole(modeling_handler, scene_handler, mesh_handler, "E2E_GridFill2")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Select boundary edges
        mesh_handler.select_all(deselect=True)
        mesh_handler.select_boundary(mode="EDGE")

        # Test grid fill with span
        result = mesh_handler.grid_fill(span=2)

        # Verify
        assert "grid filled" in result.lower()
        assert "span=2" in result
        print(f"✓ grid_fill (span=2): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_grid_fill_simple_interpolation(mesh_handler, modeling_handler, scene_handler):
    """Test grid fill with simple interpolation."""
    try:
        # Setup
        obj_name = create_mesh_with_hole(modeling_handler, scene_handler, mesh_handler, "E2E_GridFill3")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Select boundary edges
        mesh_handler.select_all(deselect=True)
        mesh_handler.select_boundary(mode="EDGE")

        # Test with simple interpolation
        result = mesh_handler.grid_fill(use_interp_simple=True)

        # Verify
        assert "grid filled" in result.lower()
        print(f"✓ grid_fill (simple interp): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ==============================================================================
# TASK-036-3: mesh_poke_faces Tests
# ==============================================================================

def test_poke_faces_default(mesh_handler, modeling_handler, scene_handler):
    """Test poke faces with default parameters."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_PokeFaces1")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test poke faces
        result = mesh_handler.poke_faces()

        # Verify
        assert "poked" in result.lower()
        print(f"✓ poke_faces (default): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_poke_faces_with_offset(mesh_handler, modeling_handler, scene_handler):
    """Test poke faces with positive offset (creates spikes)."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_PokeFaces2")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test poke with offset (creates spikes)
        result = mesh_handler.poke_faces(offset=0.5)

        # Verify
        assert "poked" in result.lower()
        assert "offset=0.5" in result
        print(f"✓ poke_faces (offset=0.5): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_poke_faces_relative_offset(mesh_handler, modeling_handler, scene_handler):
    """Test poke faces with relative offset."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_PokeFaces3")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test with relative offset
        result = mesh_handler.poke_faces(offset=0.3, use_relative_offset=True)

        # Verify
        assert "poked" in result.lower()
        assert "offset=0.3" in result
        print(f"✓ poke_faces (relative): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_poke_faces_center_mode(mesh_handler, modeling_handler, scene_handler):
    """Test poke faces with different center modes."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_PokeFaces4")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test with BOUNDS center mode
        result = mesh_handler.poke_faces(center_mode="BOUNDS")

        # Verify
        assert "poked" in result.lower()
        assert "BOUNDS" in result
        print(f"✓ poke_faces (BOUNDS mode): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_poke_faces_invalid_center_mode_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that invalid center_mode raises error."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_PokeFaces5")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test - should raise error
        mesh_handler.poke_faces(center_mode="INVALID")
        assert False, "Expected error for invalid center_mode"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid center_mode" in error_msg:
            print("✓ poke_faces properly handles invalid center_mode")
        else:
            raise
    finally:
        try:
            scene_handler.set_mode("OBJECT")
        except RuntimeError:
            pass


# ==============================================================================
# TASK-036-4: mesh_beautify_fill Tests
# ==============================================================================

def test_beautify_fill_default(mesh_handler, modeling_handler, scene_handler):
    """Test beautify fill with default angle limit."""
    try:
        # Setup
        obj_name = create_triangulated_mesh(modeling_handler, scene_handler, mesh_handler, "E2E_BeautifyFill1")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test beautify fill
        result = mesh_handler.beautify_fill()

        # Verify
        assert "beautified" in result.lower()
        assert "180.0" in result
        print(f"✓ beautify_fill (default): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_beautify_fill_custom_angle(mesh_handler, modeling_handler, scene_handler):
    """Test beautify fill with custom angle limit."""
    try:
        # Setup
        obj_name = create_triangulated_mesh(modeling_handler, scene_handler, mesh_handler, "E2E_BeautifyFill2")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test with custom angle
        result = mesh_handler.beautify_fill(angle_limit=90.0)

        # Verify
        assert "beautified" in result.lower()
        assert "90.0" in result
        print(f"✓ beautify_fill (angle=90): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_beautify_fill_small_angle(mesh_handler, modeling_handler, scene_handler):
    """Test beautify fill with small angle limit."""
    try:
        # Setup
        obj_name = create_triangulated_mesh(modeling_handler, scene_handler, mesh_handler, "E2E_BeautifyFill3")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test with small angle
        result = mesh_handler.beautify_fill(angle_limit=45.0)

        # Verify
        assert "beautified" in result.lower()
        assert "45.0" in result
        print(f"✓ beautify_fill (angle=45): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ==============================================================================
# TASK-036-5: mesh_mirror Tests
# ==============================================================================

def test_mirror_default(mesh_handler, modeling_handler, scene_handler):
    """Test mirror with default parameters (X axis)."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Mirror1")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Select half of the mesh
        mesh_handler.select_all(deselect=True)
        mesh_handler.select_by_location(axis='X', min_coord=0, max_coord=2, mode='FACE')

        # Test mirror
        result = mesh_handler.mirror()

        # Verify
        assert "mirrored" in result.lower()
        assert "X" in result
        print(f"✓ mirror (default X): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_mirror_y_axis(mesh_handler, modeling_handler, scene_handler):
    """Test mirror on Y axis."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Mirror2")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test mirror on Y
        result = mesh_handler.mirror(axis="Y")

        # Verify
        assert "mirrored" in result.lower()
        assert "Y" in result
        print(f"✓ mirror (Y axis): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_mirror_z_axis(mesh_handler, modeling_handler, scene_handler):
    """Test mirror on Z axis."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Mirror3")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test mirror on Z
        result = mesh_handler.mirror(axis="Z")

        # Verify
        assert "mirrored" in result.lower()
        assert "Z" in result
        print(f"✓ mirror (Z axis): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_mirror_with_merge(mesh_handler, modeling_handler, scene_handler):
    """Test mirror with merge enabled (default)."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Mirror4")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test mirror with merge
        result = mesh_handler.mirror(use_mirror_merge=True)

        # Verify
        assert "mirrored" in result.lower()
        assert "merged" in result.lower()
        print(f"✓ mirror (with merge): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_mirror_without_merge(mesh_handler, modeling_handler, scene_handler):
    """Test mirror without merge."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Mirror5")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test mirror without merge
        result = mesh_handler.mirror(use_mirror_merge=False)

        # Verify
        assert "mirrored" in result.lower()
        print(f"✓ mirror (no merge): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_mirror_custom_threshold(mesh_handler, modeling_handler, scene_handler):
    """Test mirror with custom merge threshold."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Mirror6")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test with custom threshold
        result = mesh_handler.mirror(merge_threshold=0.01)

        # Verify
        assert "mirrored" in result.lower()
        assert "0.01" in result
        print(f"✓ mirror (custom threshold): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_mirror_invalid_axis_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that invalid axis raises error."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Mirror7")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test - should raise error
        mesh_handler.mirror(axis="W")
        assert False, "Expected error for invalid axis"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid axis" in error_msg:
            print("✓ mirror properly handles invalid axis")
        else:
            raise
    finally:
        try:
            scene_handler.set_mode("OBJECT")
        except RuntimeError:
            pass


# ==============================================================================
# Integration Workflow Tests
# ==============================================================================

def test_workflow_character_symmetry(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Character modeling symmetry workflow.
    Create asymmetric mesh → symmetrize → verify.
    """
    try:
        # Setup: Create asymmetric mesh
        obj_name = create_asymmetric_mesh(modeling_handler, scene_handler, mesh_handler, "E2E_CharacterSymmetry")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Step 1: Symmetrize the mesh
        symmetrize_result = mesh_handler.symmetrize(direction="NEGATIVE_X")
        assert "symmetrized" in symmetrize_result.lower()
        print(f"  Step 1 - Symmetrize: {symmetrize_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Character symmetry workflow completed")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_hole_filling(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Hole filling with proper topology.
    Create mesh with hole → select boundary → grid fill.
    """
    try:
        # Setup: Create mesh with hole
        obj_name = create_mesh_with_hole(modeling_handler, scene_handler, mesh_handler, "E2E_HoleFilling")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Step 1: Select boundary
        mesh_handler.select_all(deselect=True)
        mesh_handler.select_boundary(mode="EDGE")
        print("  Step 1 - Selected boundary edges")

        # Step 2: Grid fill the hole
        fill_result = mesh_handler.grid_fill()
        assert "grid filled" in fill_result.lower()
        print(f"  Step 2 - Grid fill: {fill_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Hole filling workflow completed")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_spike_creation(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Creating spikes with poke faces.
    Create cube → poke faces with offset → creates spiky object.
    """
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_SpikeCreation")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Step 1: Subdivide for more faces
        mesh_handler.subdivide(number_cuts=2)
        print("  Step 1 - Subdivided mesh")

        # Step 2: Poke faces with offset (creates spikes)
        poke_result = mesh_handler.poke_faces(offset=0.3)
        assert "poked" in poke_result.lower()
        print(f"  Step 2 - Poke faces: {poke_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Spike creation workflow completed")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_triangle_cleanup(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Cleaning up triangulated mesh.
    Create triangulated mesh → beautify fill → tris to quads.
    """
    try:
        # Setup
        obj_name = create_triangulated_mesh(modeling_handler, scene_handler, mesh_handler, "E2E_TriangleCleanup")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Step 1: Beautify fill
        beautify_result = mesh_handler.beautify_fill(angle_limit=60.0)
        assert "beautified" in beautify_result.lower()
        print(f"  Step 1 - Beautify fill: {beautify_result}")

        # Step 2: Convert tris to quads where possible
        tris_result = mesh_handler.tris_to_quads()
        assert "converted triangles to quads" in tris_result.lower()
        print(f"  Step 2 - Tris to quads: {tris_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Triangle cleanup workflow completed")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_mirror_duplicate(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Creating mirrored duplicate.
    Select half → duplicate → mirror → merge.
    """
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_MirrorDuplicate")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Step 1: Select all
        mesh_handler.select_all(deselect=False)
        print("  Step 1 - Selected all geometry")

        # Step 2: Mirror with merge
        mirror_result = mesh_handler.mirror(axis="X", use_mirror_merge=True)
        assert "mirrored" in mirror_result.lower()
        print(f"  Step 2 - Mirror: {mirror_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Mirror duplicate workflow completed")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
