"""
E2E Tests for TASK-029: Edge Weights & Creases (Subdivision Control)

Tests require a running Blender instance with the addon loaded.
Run: pytest tests/e2e/tools/mesh/test_mesh_edge_weights.py -v

Tested tools:
- mesh_edge_crease
- mesh_bevel_weight
- mesh_mark_sharp
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

def create_test_cube(modeling_handler, scene_handler, name="E2E_EdgeWeightsCube"):
    """Creates a test cube for edge weight operations."""
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


def enter_edit_mode_and_select_edges(scene_handler, mesh_handler, object_name):
    """Enters edit mode and selects some edges."""
    # Set object as active
    scene_handler.set_active_object(object_name)

    # Enter Edit Mode
    scene_handler.set_mode("EDIT")

    # Select all edges by selecting all geometry
    mesh_handler.select_all(deselect=False)


# ==============================================================================
# TASK-029-1: mesh_edge_crease Tests
# ==============================================================================

def test_edge_crease_full_sharp(mesh_handler, modeling_handler, scene_handler):
    """Test setting full crease (1.0) on selected edges."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_EdgeCrease1")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.edge_crease(crease_value=1.0)

        # Verify
        assert "crease weight 1.0" in result.lower()
        assert "edge" in result.lower()
        print(f"✓ edge_crease (full): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_edge_crease_partial(mesh_handler, modeling_handler, scene_handler):
    """Test setting partial crease (0.5) on selected edges."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_EdgeCrease2")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.edge_crease(crease_value=0.5)

        # Verify
        assert "crease weight 0.5" in result.lower()
        print(f"✓ edge_crease (partial): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_edge_crease_remove(mesh_handler, modeling_handler, scene_handler):
    """Test removing crease (0.0) from selected edges."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_EdgeCrease3")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # First set crease
        mesh_handler.edge_crease(crease_value=1.0)

        # Then remove it
        result = mesh_handler.edge_crease(crease_value=0.0)

        # Verify
        assert "crease weight 0.0" in result.lower()
        print(f"✓ edge_crease (remove): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_edge_crease_no_selection_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that error is raised when no edges selected."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_EdgeCrease4")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Deselect all
        mesh_handler.select_all(deselect=True)

        # Test - should raise error
        mesh_handler.edge_crease(crease_value=1.0)
        assert False, "Expected error for no edges selected"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "no edges selected" in error_msg:
            print("✓ edge_crease properly handles no selection")
        else:
            raise
    finally:
        try:
            scene_handler.set_mode("OBJECT")
        except RuntimeError:
            pass


# ==============================================================================
# TASK-029-2: mesh_bevel_weight Tests
# ==============================================================================

def test_bevel_weight_full(mesh_handler, modeling_handler, scene_handler):
    """Test setting full bevel weight (1.0) on selected edges."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_BevelWeight1")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.bevel_weight(weight=1.0)

        # Verify
        assert "bevel weight 1.0" in result.lower()
        assert "edge" in result.lower()
        print(f"✓ bevel_weight (full): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_bevel_weight_partial(mesh_handler, modeling_handler, scene_handler):
    """Test setting partial bevel weight (0.5) on selected edges."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_BevelWeight2")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.bevel_weight(weight=0.5)

        # Verify
        assert "bevel weight 0.5" in result.lower()
        print(f"✓ bevel_weight (partial): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_bevel_weight_remove(mesh_handler, modeling_handler, scene_handler):
    """Test removing bevel weight (0.0) from selected edges."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_BevelWeight3")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # First set weight
        mesh_handler.bevel_weight(weight=1.0)

        # Then remove it
        result = mesh_handler.bevel_weight(weight=0.0)

        # Verify
        assert "bevel weight 0.0" in result.lower()
        print(f"✓ bevel_weight (remove): {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_bevel_weight_no_selection_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that error is raised when no edges selected."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_BevelWeight4")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Deselect all
        mesh_handler.select_all(deselect=True)

        # Test - should raise error
        mesh_handler.bevel_weight(weight=1.0)
        assert False, "Expected error for no edges selected"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "no edges selected" in error_msg:
            print("✓ bevel_weight properly handles no selection")
        else:
            raise
    finally:
        try:
            scene_handler.set_mode("OBJECT")
        except RuntimeError:
            pass


# ==============================================================================
# TASK-029-3: mesh_mark_sharp Tests
# ==============================================================================

def test_mark_sharp(mesh_handler, modeling_handler, scene_handler):
    """Test marking edges as sharp."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_MarkSharp1")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Test
        result = mesh_handler.mark_sharp(action="mark")

        # Verify
        assert "marked" in result.lower()
        assert "edge" in result.lower()
        print(f"✓ mark_sharp: {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_clear_sharp(mesh_handler, modeling_handler, scene_handler):
    """Test clearing sharp from edges."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_MarkSharp2")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # First mark as sharp
        mesh_handler.mark_sharp(action="mark")

        # Then clear
        result = mesh_handler.mark_sharp(action="clear")

        # Verify
        assert "cleared" in result.lower()
        print(f"✓ clear_sharp: {result}")

        # Cleanup
        scene_handler.set_mode("OBJECT")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_mark_sharp_no_selection_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that error is raised when no edges selected."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_MarkSharp3")
        scene_handler.set_active_object(obj_name)
        scene_handler.set_mode("EDIT")

        # Deselect all
        mesh_handler.select_all(deselect=True)

        # Test - should raise error
        mesh_handler.mark_sharp(action="mark")
        assert False, "Expected error for no edges selected"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "no edges selected" in error_msg:
            print("✓ mark_sharp properly handles no selection")
        else:
            raise
    finally:
        try:
            scene_handler.set_mode("OBJECT")
        except RuntimeError:
            pass


def test_mark_sharp_invalid_action_raises(mesh_handler, modeling_handler, scene_handler):
    """Test that invalid action raises error."""
    try:
        # Setup
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_MarkSharp4")
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Test - should raise error
        mesh_handler.mark_sharp(action="invalid")
        assert False, "Expected error for invalid action"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid action" in error_msg:
            print("✓ mark_sharp properly handles invalid action")
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

def test_workflow_crease_with_subsurf(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Create cube → set crease → add Subsurf → verify sharp corners.
    This is the typical workflow for hard-surface modeling.
    """
    try:
        # Setup: Create cube
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_CreaseWorkflow")

        # Enter Edit Mode and select edges
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Set crease on all edges
        crease_result = mesh_handler.edge_crease(crease_value=1.0)
        assert "crease weight 1.0" in crease_result.lower()

        # Return to Object Mode
        scene_handler.set_mode("OBJECT")

        # Add Subdivision Surface modifier
        modifier_result = modeling_handler.add_modifier(
            object_name=obj_name,
            modifier_type="SUBSURF",
            levels=2,
            render_levels=2
        )
        assert "SUBSURF" in modifier_result or "Subsurf" in modifier_result or "added" in modifier_result.lower()

        print(f"✓ Crease + Subsurf workflow completed: {crease_result}, {modifier_result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_bevel_weight_with_bevel_modifier(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Create cube → set bevel weight → add Bevel modifier (weight mode).
    This is the typical workflow for selective beveling.
    """
    try:
        # Setup: Create cube
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_BevelWorkflow")

        # Enter Edit Mode and select some edges
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Set bevel weight
        bevel_result = mesh_handler.bevel_weight(weight=1.0)
        assert "bevel weight 1.0" in bevel_result.lower()

        # Return to Object Mode
        scene_handler.set_mode("OBJECT")

        # Add Bevel modifier with Weight limit method
        modifier_result = modeling_handler.add_modifier(
            object_name=obj_name,
            modifier_type="BEVEL",
            width=0.1,
            segments=2,
            limit_method="WEIGHT"
        )
        assert "BEVEL" in modifier_result or "Bevel" in modifier_result or "added" in modifier_result.lower()

        print(f"✓ Bevel weight + Bevel modifier workflow completed: {bevel_result}, {modifier_result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_workflow_mark_sharp_with_auto_smooth(mesh_handler, modeling_handler, scene_handler):
    """
    Integration test: Create cube → mark edges as sharp → verify marking.
    Sharp edges affect Auto Smooth and Edge Split modifier.
    """
    try:
        # Setup: Create cube
        obj_name = create_test_cube(modeling_handler, scene_handler, "E2E_SharpWorkflow")

        # Enter Edit Mode and select edges
        enter_edit_mode_and_select_edges(scene_handler, mesh_handler, obj_name)

        # Mark as sharp
        sharp_result = mesh_handler.mark_sharp(action="mark")
        assert "marked" in sharp_result.lower()

        # Return to Object Mode
        scene_handler.set_mode("OBJECT")

        print(f"✓ Mark sharp workflow completed: {sharp_result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
