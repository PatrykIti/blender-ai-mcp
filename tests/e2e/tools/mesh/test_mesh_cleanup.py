"""
E2E Tests for TASK-030: Mesh Cleanup & Optimization

Tests require a running Blender instance with the addon loaded.
Run: pytest tests/e2e/tools/mesh/test_mesh_cleanup.py -v

Tested tools:
- mesh_dissolve
- mesh_tris_to_quads
- mesh_normals_make_consistent
- mesh_decimate
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

def create_test_cube(modeling_handler, scene_handler, name="E2E_CleanupCube"):
    """Creates a test cube for cleanup operations."""
    try:
        # Clean up existing
        scene_handler.delete_object(name)
    except RuntimeError:
        pass  # Object didn't exist

    # Create cube
    result = modeling_handler.create_primitive(
        primitive_type="CUBE",
        size=2.0,
        location=[0, 0, 0],
        name=name
    )
    return name


def create_test_icosphere(modeling_handler, scene_handler, name="E2E_CleanupSphere", subdivisions=3):
    """Creates a test icosphere (triangulated mesh) for cleanup operations."""
    try:
        # Clean up existing
        scene_handler.delete_object(name)
    except RuntimeError:
        pass  # Object didn't exist

    # Create icosphere (produces triangles)
    result = modeling_handler.create_primitive(
        primitive_type="ICO_SPHERE",
        subdivisions=subdivisions,
        location=[0, 0, 0],
        name=name
    )
    return name


def enter_edit_mode_and_select_all(scene_handler, mesh_handler, object_name):
    """Enters edit mode and selects all geometry."""
    # Set object as active
    scene_handler.set_active_object(object_name)

    # Enter Edit Mode
    scene_handler.set_mode("EDIT")

    # Select all geometry
    mesh_handler.select_all(deselect=False)


# ==============================================================================
# TASK-030-1: mesh_dissolve Tests
# ==============================================================================

def test_dissolve_limited_default(mesh_handler, modeling_handler, scene_handler):
    """Test limited dissolve with default parameters."""
    try:
        # Setup: Create a subdivided cube for more geometry
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Dissolve1")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Subdivide first to have more geometry to dissolve
        mesh_handler.subdivide(number_cuts=2)

        # Test limited dissolve
        result = mesh_handler.dissolve()

        # Verify
        assert "limited dissolve" in result.lower() or "completed" in result.lower()
        print(f"✓ dissolve (limited): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_dissolve_limited_custom_angle(mesh_handler, modeling_handler, scene_handler):
    """Test limited dissolve with custom angle."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Dissolve2")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Subdivide
        mesh_handler.subdivide(number_cuts=2)

        # Test limited dissolve with custom angle
        result = mesh_handler.dissolve(dissolve_type="limited", angle_limit=15.0)

        # Verify
        assert "15.0" in result or "completed" in result.lower()
        print(f"✓ dissolve (limited, 15°): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_dissolve_verts(mesh_handler, modeling_handler, scene_handler):
    """Test dissolve vertices."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Dissolve3")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Subdivide to have vertices to dissolve
        mesh_handler.subdivide(number_cuts=1)

        # Deselect all, then select center vertices
        mesh_handler.select_all(deselect=True)
        mesh_handler.select_by_location(axis='Z', min_coord=-0.5, max_coord=0.5, mode='VERT')

        # Test dissolve verts
        result = mesh_handler.dissolve(dissolve_type="verts")

        # Verify
        assert "dissolved selected vertices" in result.lower() or "completed" in result.lower()
        print(f"✓ dissolve (verts): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_dissolve_invalid_type_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that invalid dissolve_type raises error."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Dissolve4")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test - should raise error
        mesh_handler.dissolve(dissolve_type="invalid")
        assert False, "Expected error for invalid dissolve_type"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid dissolve_type" in error_msg:
            print("✓ dissolve properly handles invalid type")
        else:
            raise
    finally:
        try:
            scene_handler.set_mode("OBJECT")
        except RuntimeError:
            pass


# ==============================================================================
# TASK-030-2: mesh_tris_to_quads Tests
# ==============================================================================

def test_tris_to_quads_default(mesh_handler, modeling_handler, scene_handler):
    """Test tris to quads conversion with default thresholds."""
    try:
        # Setup: Create icosphere (triangulated)
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_TrisToQuads1")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test tris to quads
        result = mesh_handler.tris_to_quads()

        # Verify
        assert "converted triangles to quads" in result.lower()
        print(f"✓ tris_to_quads (default): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_tris_to_quads_custom_thresholds(mesh_handler, modeling_handler, scene_handler):
    """Test tris to quads conversion with custom thresholds."""
    try:
        # Setup: Create icosphere
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_TrisToQuads2")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test with custom thresholds
        result = mesh_handler.tris_to_quads(face_threshold=30.0, shape_threshold=50.0)

        # Verify
        assert "face threshold: 30.0" in result
        assert "shape threshold: 50.0" in result
        print(f"✓ tris_to_quads (custom): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_tris_to_quads_already_quads(mesh_handler, modeling_handler, scene_handler):
    """Test tris to quads on cube (already quads) - should succeed with no error."""
    try:
        # Setup: Create cube (already quads)
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_TrisToQuads3")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test - should succeed even though there are no tris
        result = mesh_handler.tris_to_quads()

        # Verify - operation should complete without error
        assert "converted triangles to quads" in result.lower()
        print(f"✓ tris_to_quads (no tris): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ==============================================================================
# TASK-030-3: mesh_normals_make_consistent Tests
# ==============================================================================

def test_normals_make_consistent_outward(mesh_handler, modeling_handler, scene_handler):
    """Test normals make consistent outward (default)."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Normals1")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.normals_make_consistent()

        # Verify
        assert "outward" in result.lower()
        print(f"✓ normals_make_consistent (outward): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_normals_make_consistent_inward(mesh_handler, modeling_handler, scene_handler):
    """Test normals make consistent inward."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Normals2")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.normals_make_consistent(inside=True)

        # Verify
        assert "inward" in result.lower()
        print(f"✓ normals_make_consistent (inward): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_normals_on_complex_mesh(mesh_handler, modeling_handler, scene_handler):
    """Test normals on more complex mesh (icosphere)."""
    try:
        # Setup
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_Normals3")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.normals_make_consistent()

        # Verify
        assert "outward" in result.lower() or "consistently" in result.lower()
        print(f"✓ normals_make_consistent (icosphere): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ==============================================================================
# TASK-030-4: mesh_decimate Tests
# ==============================================================================

def test_decimate_default(mesh_handler, modeling_handler, scene_handler):
    """Test decimate with default ratio (50%)."""
    try:
        # Setup: Create icosphere with more geometry
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_Decimate1", subdivisions=3)
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.decimate()

        # Verify
        assert "50.0%" in result or "decimated" in result.lower()
        print(f"✓ decimate (default 50%): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_decimate_custom_ratio(mesh_handler, modeling_handler, scene_handler):
    """Test decimate with custom ratio (25%)."""
    try:
        # Setup
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_Decimate2", subdivisions=3)
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.decimate(ratio=0.25)

        # Verify
        assert "25.0%" in result
        print(f"✓ decimate (25%): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_decimate_with_symmetry(mesh_handler, modeling_handler, scene_handler):
    """Test decimate with symmetry enabled."""
    try:
        # Setup
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_Decimate3", subdivisions=3)
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.decimate(ratio=0.5, use_symmetry=True, symmetry_axis='X')

        # Verify
        assert "x symmetry" in result.lower()
        print(f"✓ decimate (with symmetry): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_decimate_invalid_axis_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that invalid symmetry axis raises error."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_Decimate4")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Test - should raise error
        mesh_handler.decimate(use_symmetry=True, symmetry_axis='W')
        assert False, "Expected error for invalid axis"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid symmetry_axis" in error_msg:
            print("✓ decimate properly handles invalid axis")
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

def test_workflow_cleanup_imported_mesh(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Simulates cleaning up an imported mesh.
    Create triangulated mesh → tris to quads → normals → dissolve.
    """
    try:
        # Setup: Create icosphere (simulating imported triangulated mesh)
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_CleanupWorkflow")
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Step 1: Convert triangles to quads where possible
        tris_result = mesh_handler.tris_to_quads(face_threshold=40.0, shape_threshold=40.0)
        assert "converted triangles to quads" in tris_result.lower()
        print(f"  Step 1 - Tris to Quads: {tris_result}")

        # Step 2: Make normals consistent
        normals_result = mesh_handler.normals_make_consistent()
        assert "outward" in normals_result.lower()
        print(f"  Step 2 - Normals: {normals_result}")

        # Step 3: Limited dissolve to simplify
        dissolve_result = mesh_handler.dissolve(dissolve_type="limited", angle_limit=10.0)
        assert "limited dissolve" in dissolve_result.lower() or "completed" in dissolve_result.lower()
        print(f"  Step 3 - Dissolve: {dissolve_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Cleanup workflow completed successfully")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_optimize_high_poly(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Optimize high-poly mesh for game engine.
    Create detailed mesh → decimate → clean up → normals.
    """
    try:
        # Setup: Create high-poly icosphere
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_OptimizeWorkflow", subdivisions=4)
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Step 1: Decimate to reduce polycount
        decimate_result = mesh_handler.decimate(ratio=0.3)
        assert "30.0%" in decimate_result or "decimated" in decimate_result.lower()
        print(f"  Step 1 - Decimate: {decimate_result}")

        # Step 2: Make normals consistent after decimation
        normals_result = mesh_handler.normals_make_consistent()
        assert "outward" in normals_result.lower()
        print(f"  Step 2 - Normals: {normals_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Optimization workflow completed successfully")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_retopology_preparation(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Prepare mesh for retopology.
    Create mesh → tris to quads → dissolve edges → decimate.
    """
    try:
        # Setup
        obj_name = create_test_icosphere(modeling_handler, scene_handler, "E2E_RetopoWorkflow", subdivisions=3)
        enter_edit_mode_and_select_all(scene_handler, mesh_handler, obj_name)

        # Step 1: Convert triangles to quads
        tris_result = mesh_handler.tris_to_quads()
        print(f"  Step 1 - Tris to Quads: {tris_result}")

        # Step 2: Limited dissolve to simplify topology
        dissolve_result = mesh_handler.dissolve(dissolve_type="limited", angle_limit=5.0)
        print(f"  Step 2 - Dissolve: {dissolve_result}")

        # Step 3: Decimate to target polycount
        decimate_result = mesh_handler.decimate(ratio=0.5)
        print(f"  Step 3 - Decimate: {decimate_result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
        print("✓ Retopology preparation workflow completed")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
