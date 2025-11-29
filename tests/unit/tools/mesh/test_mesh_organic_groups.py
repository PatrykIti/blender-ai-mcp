"""
Tests for TASK-016 (Organic & Deform) and TASK-017 (Vertex Groups) tools.
Pure pytest style - uses conftest.py fixtures.
"""
import pytest
from unittest.mock import MagicMock

import bpy
import bmesh

from blender_addon.application.handlers.mesh import MeshHandler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mesh_handler():
    """Provides a fresh MeshHandler instance."""
    return MeshHandler()


@pytest.fixture
def mock_edit_mode():
    """Sets up basic edit mode mocks."""
    bpy.context.active_object = MagicMock()
    bpy.context.active_object.type = 'MESH'
    bpy.context.active_object.mode = 'EDIT'
    bpy.ops.object.mode_set = MagicMock()
    return bpy.context.active_object


@pytest.fixture
def mock_bmesh_with_selection():
    """Sets up bmesh with selected vertices."""
    mock_bm = MagicMock()
    mock_vert = MagicMock()
    mock_vert.select = True
    mock_vert.index = 0
    mock_bm.verts = [mock_vert]
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_bmesh_empty():
    """Sets up bmesh with no selected vertices."""
    mock_bm = MagicMock()
    mock_bm.verts = []
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_mesh_object():
    """Sets up a mock mesh object with vertex groups."""
    mock_obj = MagicMock()
    mock_obj.type = 'MESH'
    mock_obj.mode = 'EDIT'

    mock_vg = MagicMock()
    mock_vg.name = "TestGroup"
    mock_vg.index = 0
    mock_vg.add = MagicMock()

    mock_obj.vertex_groups = MagicMock()
    mock_obj.vertex_groups.__contains__ = MagicMock(return_value=False)
    mock_obj.vertex_groups.__getitem__ = MagicMock(return_value=mock_vg)
    mock_obj.vertex_groups.new = MagicMock(return_value=mock_vg)

    bpy.data.objects = MagicMock()
    bpy.data.objects.__contains__ = MagicMock(return_value=True)
    bpy.data.objects.__getitem__ = MagicMock(return_value=mock_obj)

    bpy.context.view_layer.objects.active = mock_obj
    bpy.ops.object.mode_set = MagicMock()

    return mock_obj


# =============================================================================
# TASK-016-1: mesh_randomize tests
# =============================================================================

class TestMeshRandomize:
    """Tests for mesh_randomize tool."""

    def test_randomize_default_params(self, mesh_handler, mock_edit_mode, mock_bmesh_with_selection):
        """Should randomize with default parameters."""
        bpy.ops.transform.vertex_random = MagicMock()

        result = mesh_handler.randomize()

        bpy.ops.transform.vertex_random.assert_called_with(
            offset=0.1,
            uniform=0.0,
            normal=0.0,
            seed=0
        )
        assert "Randomized" in result

    def test_randomize_custom_params(self, mesh_handler, mock_edit_mode, mock_bmesh_with_selection):
        """Should randomize with custom parameters."""
        bpy.ops.transform.vertex_random = MagicMock()

        result = mesh_handler.randomize(amount=0.5, uniform=0.3, normal=0.7, seed=42)

        bpy.ops.transform.vertex_random.assert_called_with(
            offset=0.5,
            uniform=0.3,
            normal=0.7,
            seed=42
        )
        assert "amount=0.5" in result

    def test_randomize_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no vertices selected."""
        with pytest.raises(ValueError, match="No vertices selected"):
            mesh_handler.randomize()


# =============================================================================
# TASK-016-2: mesh_shrink_fatten tests
# =============================================================================

class TestMeshShrinkFatten:
    """Tests for mesh_shrink_fatten tool."""

    def test_shrink_fatten_positive(self, mesh_handler, mock_edit_mode, mock_bmesh_with_selection):
        """Should fatten (positive value)."""
        bpy.ops.transform.shrink_fatten = MagicMock()

        result = mesh_handler.shrink_fatten(value=0.2)

        bpy.ops.transform.shrink_fatten.assert_called_with(value=0.2)
        assert "fattened" in result

    def test_shrink_fatten_negative(self, mesh_handler, mock_edit_mode, mock_bmesh_with_selection):
        """Should shrink (negative value)."""
        bpy.ops.transform.shrink_fatten = MagicMock()

        result = mesh_handler.shrink_fatten(value=-0.1)

        bpy.ops.transform.shrink_fatten.assert_called_with(value=-0.1)
        assert "shrunk" in result

    def test_shrink_fatten_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no vertices selected."""
        with pytest.raises(ValueError, match="No vertices selected"):
            mesh_handler.shrink_fatten(value=0.1)


# =============================================================================
# TASK-017-1: mesh_create_vertex_group tests
# =============================================================================

class TestMeshCreateVertexGroup:
    """Tests for mesh_create_vertex_group tool."""

    def test_create_vertex_group_success(self, mesh_handler, mock_mesh_object):
        """Should create vertex group successfully."""
        result = mesh_handler.create_vertex_group("TestMesh", "TestGroup")

        mock_mesh_object.vertex_groups.new.assert_called_with(name="TestGroup")
        assert "Created vertex group" in result
        assert "TestGroup" in result

    def test_create_vertex_group_object_not_found(self, mesh_handler):
        """Should raise ValueError when object not found."""
        bpy.data.objects = MagicMock()
        bpy.data.objects.__contains__ = MagicMock(return_value=False)

        with pytest.raises(ValueError, match="not found"):
            mesh_handler.create_vertex_group("NonExistent", "TestGroup")

    def test_create_vertex_group_not_mesh(self, mesh_handler, mock_mesh_object):
        """Should raise ValueError when object is not a mesh."""
        mock_mesh_object.type = 'CURVE'

        with pytest.raises(ValueError, match="not a MESH"):
            mesh_handler.create_vertex_group("TestCurve", "TestGroup")

    def test_create_vertex_group_already_exists(self, mesh_handler, mock_mesh_object):
        """Should raise ValueError when group already exists."""
        mock_mesh_object.vertex_groups.__contains__ = MagicMock(return_value=True)

        with pytest.raises(ValueError, match="already exists"):
            mesh_handler.create_vertex_group("TestMesh", "ExistingGroup")


# =============================================================================
# TASK-017-2: mesh_assign_to_group tests
# =============================================================================

class TestMeshAssignToGroup:
    """Tests for mesh_assign_to_group tool."""

    def test_assign_to_group_success(self, mesh_handler, mock_mesh_object, mock_bmesh_with_selection):
        """Should assign vertices to group."""
        mock_mesh_object.vertex_groups.__contains__ = MagicMock(return_value=True)
        bpy.ops.object.vertex_group_assign = MagicMock()

        result = mesh_handler.assign_to_group("TestMesh", "TestGroup", weight=1.0)

        bpy.ops.object.vertex_group_assign.assert_called()
        assert "Assigned" in result
        assert "TestGroup" in result

    def test_assign_to_group_custom_weight(self, mesh_handler, mock_mesh_object, mock_bmesh_with_selection):
        """Should assign with custom weight."""
        mock_mesh_object.vertex_groups.__contains__ = MagicMock(return_value=True)
        bpy.ops.object.vertex_group_assign = MagicMock()

        result = mesh_handler.assign_to_group("TestMesh", "TestGroup", weight=0.5)

        assert "weight 0.5" in result

    def test_assign_to_group_no_selection_raises(self, mesh_handler, mock_mesh_object, mock_bmesh_empty):
        """Should raise ValueError when no vertices selected."""
        mock_mesh_object.vertex_groups.__contains__ = MagicMock(return_value=True)

        with pytest.raises(ValueError, match="No vertices selected"):
            mesh_handler.assign_to_group("TestMesh", "TestGroup")


# =============================================================================
# TASK-017-2: mesh_remove_from_group tests
# =============================================================================

class TestMeshRemoveFromGroup:
    """Tests for mesh_remove_from_group tool."""

    def test_remove_from_group_success(self, mesh_handler, mock_mesh_object, mock_bmesh_with_selection):
        """Should remove vertices from group."""
        mock_mesh_object.vertex_groups.__contains__ = MagicMock(return_value=True)
        bpy.ops.object.vertex_group_remove_from = MagicMock()

        result = mesh_handler.remove_from_group("TestMesh", "TestGroup")

        bpy.ops.object.vertex_group_remove_from.assert_called()
        assert "Removed" in result
        assert "TestGroup" in result

    def test_remove_from_group_no_selection_raises(self, mesh_handler, mock_mesh_object, mock_bmesh_empty):
        """Should raise ValueError when no vertices selected."""
        mock_mesh_object.vertex_groups.__contains__ = MagicMock(return_value=True)

        with pytest.raises(ValueError, match="No vertices selected"):
            mesh_handler.remove_from_group("TestMesh", "TestGroup")

    def test_remove_from_group_not_found(self, mesh_handler, mock_mesh_object, mock_bmesh_with_selection):
        """Should raise ValueError when group not found."""
        mock_mesh_object.vertex_groups.__contains__ = MagicMock(return_value=False)

        with pytest.raises(ValueError, match="not found"):
            mesh_handler.remove_from_group("TestMesh", "NonExistent")
