"""
Tests for TASK-021 (Phase 2.6 - Curves & Procedural) mesh tools.
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
def mock_bmesh_with_verts():
    """Sets up bmesh with selected vertices."""
    mock_bm = MagicMock()
    mock_vert = MagicMock()
    mock_vert.select = True
    mock_vert.index = 0
    # Use MagicMock for verts so we can add .new() method
    mock_verts = MagicMock()
    mock_verts.__iter__ = MagicMock(return_value=iter([mock_vert]))
    mock_bm.verts = mock_verts
    mock_bm.edges = []
    mock_bm.faces = []
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    bmesh.update_edit_mesh = MagicMock()
    return mock_bm


@pytest.fixture
def mock_bmesh_with_two_verts():
    """Sets up bmesh with two selected vertices."""
    mock_bm = MagicMock()
    mock_vert1 = MagicMock()
    mock_vert1.select = True
    mock_vert2 = MagicMock()
    mock_vert2.select = True
    mock_bm.verts = [mock_vert1, mock_vert2]
    mock_bm.edges = []
    mock_bm.faces = []
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_bmesh_empty():
    """Sets up bmesh with no selected elements."""
    mock_bm = MagicMock()
    mock_bm.verts = []
    mock_bm.edges = []
    mock_bm.faces = []
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_scene_with_cursor():
    """Sets up scene with 3D cursor."""
    bpy.context.scene = MagicMock()
    bpy.context.scene.cursor = MagicMock()
    bpy.context.scene.cursor.location = (0, 0, 0)
    return bpy.context.scene


# =============================================================================
# TASK-021-3: mesh_spin tests
# =============================================================================

class TestMeshSpin:
    """Tests for mesh_spin tool."""

    def test_spin_default(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should spin with default parameters."""
        bpy.ops.mesh.spin = MagicMock()

        result = mesh_handler.spin()

        bpy.ops.mesh.spin.assert_called_with(
            steps=12,
            angle=6.283185,
            center=(0, 0, 0),
            axis=(0, 0, 1),  # Z axis
            dupli=False
        )
        assert "Spin complete" in result

    def test_spin_custom_steps(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should spin with custom steps."""
        bpy.ops.mesh.spin = MagicMock()

        result = mesh_handler.spin(steps=32)

        bpy.ops.mesh.spin.assert_called()
        assert "32 steps" in result

    def test_spin_half_circle(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should spin 180 degrees."""
        bpy.ops.mesh.spin = MagicMock()

        result = mesh_handler.spin(angle=3.14159)

        bpy.ops.mesh.spin.assert_called()
        assert "180" in result  # 180 degrees

    def test_spin_around_x_axis(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should spin around X axis."""
        bpy.ops.mesh.spin = MagicMock()

        result = mesh_handler.spin(axis='X')

        call_args = bpy.ops.mesh.spin.call_args
        assert call_args[1]['axis'] == (1, 0, 0)
        assert "around X" in result

    def test_spin_with_custom_center(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should spin around custom center."""
        bpy.ops.mesh.spin = MagicMock()

        result = mesh_handler.spin(center=[1, 2, 3])

        call_args = bpy.ops.mesh.spin.call_args
        assert call_args[1]['center'] == (1, 2, 3)
        assert "[1, 2, 3]" in result

    def test_spin_dupli_mode(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should spin in duplicate mode."""
        bpy.ops.mesh.spin = MagicMock()

        result = mesh_handler.spin(dupli=True)

        call_args = bpy.ops.mesh.spin.call_args
        assert call_args[1]['dupli'] == True
        assert "duplicate mode" in result

    def test_spin_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty, mock_scene_with_cursor):
        """Should raise ValueError when no geometry selected."""
        with pytest.raises(ValueError, match="No geometry selected"):
            mesh_handler.spin()

    def test_spin_invalid_axis_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should raise ValueError for invalid axis."""
        with pytest.raises(ValueError, match="Invalid axis"):
            mesh_handler.spin(axis='W')


# =============================================================================
# TASK-021-4: mesh_screw tests
# =============================================================================

class TestMeshScrew:
    """Tests for mesh_screw tool."""

    def test_screw_default(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should screw with default parameters."""
        bpy.ops.mesh.screw = MagicMock()

        result = mesh_handler.screw()

        bpy.ops.mesh.screw.assert_called_with(
            steps=12,
            turns=1,
            center=(0, 0, 0),
            axis=(0, 0, 1),
            screw_offset=0.0
        )
        assert "Screw complete" in result

    def test_screw_multiple_turns(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should screw with multiple turns."""
        bpy.ops.mesh.screw = MagicMock()

        result = mesh_handler.screw(turns=3)

        call_args = bpy.ops.mesh.screw.call_args
        assert call_args[1]['turns'] == 3
        assert "3 turn(s)" in result

    def test_screw_with_offset(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should screw with offset (pitch)."""
        bpy.ops.mesh.screw = MagicMock()

        result = mesh_handler.screw(offset=0.5)

        call_args = bpy.ops.mesh.screw.call_args
        assert call_args[1]['screw_offset'] == 0.5
        assert "offset=0.5" in result

    def test_screw_around_y_axis(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_cursor):
        """Should screw around Y axis."""
        bpy.ops.mesh.screw = MagicMock()

        result = mesh_handler.screw(axis='Y')

        call_args = bpy.ops.mesh.screw.call_args
        assert call_args[1]['axis'] == (0, 1, 0)
        assert "around Y" in result

    def test_screw_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty, mock_scene_with_cursor):
        """Should raise ValueError when no geometry selected."""
        with pytest.raises(ValueError, match="No geometry selected"):
            mesh_handler.screw()


# =============================================================================
# TASK-021-5: mesh_add_vertex tests
# =============================================================================

class TestMeshAddVertex:
    """Tests for mesh_add_vertex tool."""

    def test_add_vertex_basic(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should add vertex at specified position."""
        mock_new_vert = MagicMock()
        mock_new_vert.index = 5
        mock_bm = bmesh.from_edit_mesh.return_value
        mock_bm.verts.new = MagicMock(return_value=mock_new_vert)

        result = mesh_handler.add_vertex([1, 2, 3])

        mock_bm.verts.new.assert_called_with([1, 2, 3])
        bmesh.update_edit_mesh.assert_called()
        assert "Added vertex" in result
        assert "[1, 2, 3]" in result

    def test_add_vertex_at_origin(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should add vertex at origin."""
        mock_new_vert = MagicMock()
        mock_new_vert.index = 0
        mock_bm = bmesh.from_edit_mesh.return_value
        mock_bm.verts.new = MagicMock(return_value=mock_new_vert)

        result = mesh_handler.add_vertex([0, 0, 0])

        mock_bm.verts.new.assert_called_with([0, 0, 0])
        assert "Added vertex" in result

    def test_add_vertex_invalid_position_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should raise ValueError for invalid position."""
        with pytest.raises(ValueError, match="position must be"):
            mesh_handler.add_vertex([0, 0])  # Only 2 coordinates


# =============================================================================
# TASK-021-5: mesh_add_edge_face tests
# =============================================================================

class TestMeshAddEdgeFace:
    """Tests for mesh_add_edge_face tool."""

    def test_add_edge_from_two_verts(self, mesh_handler, mock_edit_mode, mock_bmesh_with_two_verts):
        """Should create edge from 2 selected vertices."""
        bpy.ops.mesh.edge_face_add = MagicMock()

        result = mesh_handler.add_edge_face()

        bpy.ops.mesh.edge_face_add.assert_called()
        assert "Created edge" in result

    def test_add_face_from_three_plus_verts(self, mesh_handler, mock_edit_mode):
        """Should create face from 3+ selected vertices."""
        mock_bm = MagicMock()
        mock_bm.verts = [
            MagicMock(select=True),
            MagicMock(select=True),
            MagicMock(select=True),
            MagicMock(select=True)
        ]
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
        bpy.ops.mesh.edge_face_add = MagicMock()

        result = mesh_handler.add_edge_face()

        bpy.ops.mesh.edge_face_add.assert_called()
        assert "Created face" in result

    def test_add_edge_face_insufficient_verts_raises(self, mesh_handler, mock_edit_mode):
        """Should raise ValueError when less than 2 vertices selected."""
        mock_bm = MagicMock()
        mock_bm.verts = [MagicMock(select=True)]  # Only 1 vertex
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

        with pytest.raises(ValueError, match="Select at least 2 vertices"):
            mesh_handler.add_edge_face()

    def test_add_edge_face_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no vertices selected."""
        with pytest.raises(ValueError, match="Select at least 2 vertices"):
            mesh_handler.add_edge_face()
