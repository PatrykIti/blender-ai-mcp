"""
Tests for TASK-019 (Phase 2.4 - Core Transform & Geometry) tools.
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
    mock_bm.verts = [mock_vert]
    mock_bm.edges = []
    mock_bm.faces = []
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_bmesh_with_edges():
    """Sets up bmesh with selected edges."""
    mock_bm = MagicMock()
    mock_edge = MagicMock()
    mock_edge.select = True
    mock_bm.edges = [mock_edge, mock_edge]  # At least 2 edges for bridging
    mock_bm.verts = [MagicMock(select=True)]
    mock_bm.faces = []
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_bmesh_with_faces():
    """Sets up bmesh with selected faces."""
    mock_bm = MagicMock()
    mock_face = MagicMock()
    mock_face.select = True
    mock_bm.faces = [mock_face]
    mock_bm.verts = [MagicMock(select=True)]
    mock_bm.edges = [MagicMock(select=True)]
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
def mock_scene_with_pivot():
    """Sets up scene with pivot point settings."""
    bpy.context.scene = MagicMock()
    bpy.context.scene.tool_settings = MagicMock()
    bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
    return bpy.context.scene


# =============================================================================
# TASK-019-1: mesh_transform_selected tests
# =============================================================================

class TestMeshTransformSelected:
    """Tests for mesh_transform_selected tool."""

    def test_transform_translate(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_pivot):
        """Should translate selected geometry."""
        bpy.ops.transform.translate = MagicMock()
        bpy.ops.transform.rotate = MagicMock()
        bpy.ops.transform.resize = MagicMock()

        result = mesh_handler.transform_selected(translate=[1, 2, 3])

        bpy.ops.transform.translate.assert_called_with(value=(1, 2, 3))
        assert "translated" in result
        assert "Transformed" in result

    def test_transform_rotate(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_pivot):
        """Should rotate selected geometry."""
        bpy.ops.transform.translate = MagicMock()
        bpy.ops.transform.rotate = MagicMock()
        bpy.ops.transform.resize = MagicMock()

        result = mesh_handler.transform_selected(rotate=[0, 0, 1.5708])

        bpy.ops.transform.rotate.assert_called_with(value=1.5708, orient_axis='Z')
        assert "rotated" in result

    def test_transform_scale(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_pivot):
        """Should scale selected geometry."""
        bpy.ops.transform.translate = MagicMock()
        bpy.ops.transform.rotate = MagicMock()
        bpy.ops.transform.resize = MagicMock()

        result = mesh_handler.transform_selected(scale=[2, 2, 1])

        bpy.ops.transform.resize.assert_called_with(value=(2, 2, 1))
        assert "scaled" in result

    def test_transform_sets_pivot(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_pivot):
        """Should set pivot point during transformation."""
        bpy.ops.transform.translate = MagicMock()

        result = mesh_handler.transform_selected(translate=[1, 0, 0], pivot='CURSOR')

        # Pivot is restored after transformation, so check the result message
        assert "pivot: CURSOR" in result

    def test_transform_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty, mock_scene_with_pivot):
        """Should raise ValueError when no geometry selected."""
        with pytest.raises(ValueError, match="No geometry selected"):
            mesh_handler.transform_selected(translate=[1, 0, 0])

    def test_transform_no_params_returns_message(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts, mock_scene_with_pivot):
        """Should return message when no transformation parameters provided."""
        bpy.ops.transform.translate = MagicMock()
        bpy.ops.transform.rotate = MagicMock()
        bpy.ops.transform.resize = MagicMock()

        result = mesh_handler.transform_selected()

        assert "No transformation applied" in result


# =============================================================================
# TASK-019-2: mesh_bridge_edge_loops tests
# =============================================================================

class TestMeshBridgeEdgeLoops:
    """Tests for mesh_bridge_edge_loops tool."""

    def test_bridge_basic(self, mesh_handler, mock_edit_mode, mock_bmesh_with_edges):
        """Should bridge edge loops with default parameters."""
        bpy.ops.mesh.bridge_edge_loops = MagicMock()

        result = mesh_handler.bridge_edge_loops()

        bpy.ops.mesh.bridge_edge_loops.assert_called_with(
            type='LINEAR',
            number_cuts=0,
            smoothness=0.0,
            twist_offset=0
        )
        assert "Bridged" in result

    def test_bridge_with_cuts(self, mesh_handler, mock_edit_mode, mock_bmesh_with_edges):
        """Should bridge with subdivision cuts."""
        bpy.ops.mesh.bridge_edge_loops = MagicMock()

        result = mesh_handler.bridge_edge_loops(number_cuts=4)

        bpy.ops.mesh.bridge_edge_loops.assert_called_with(
            type='LINEAR',
            number_cuts=4,
            smoothness=0.0,
            twist_offset=0
        )
        assert "cuts=4" in result

    def test_bridge_surface_interpolation(self, mesh_handler, mock_edit_mode, mock_bmesh_with_edges):
        """Should bridge with surface interpolation."""
        bpy.ops.mesh.bridge_edge_loops = MagicMock()

        result = mesh_handler.bridge_edge_loops(interpolation='SURFACE', smoothness=1.0)

        bpy.ops.mesh.bridge_edge_loops.assert_called_with(
            type='SURFACE',
            number_cuts=0,
            smoothness=1.0,
            twist_offset=0
        )
        assert "interpolation=SURFACE" in result

    def test_bridge_with_twist(self, mesh_handler, mock_edit_mode, mock_bmesh_with_edges):
        """Should bridge with twist offset."""
        bpy.ops.mesh.bridge_edge_loops = MagicMock()

        result = mesh_handler.bridge_edge_loops(twist=2)

        bpy.ops.mesh.bridge_edge_loops.assert_called_with(
            type='LINEAR',
            number_cuts=0,
            smoothness=0.0,
            twist_offset=2
        )
        assert "twist=2" in result

    def test_bridge_insufficient_edges_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when not enough edges selected."""
        with pytest.raises(ValueError, match="Select at least two edge loops"):
            mesh_handler.bridge_edge_loops()


# =============================================================================
# TASK-019-3: mesh_duplicate_selected tests
# =============================================================================

class TestMeshDuplicateSelected:
    """Tests for mesh_duplicate_selected tool."""

    def test_duplicate_basic(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should duplicate selected geometry."""
        bpy.ops.mesh.duplicate = MagicMock()

        result = mesh_handler.duplicate_selected()

        bpy.ops.mesh.duplicate.assert_called()
        assert "Duplicated" in result

    def test_duplicate_with_translate(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should duplicate and translate geometry."""
        bpy.ops.mesh.duplicate_move = MagicMock()

        result = mesh_handler.duplicate_selected(translate=[2, 0, 0])

        bpy.ops.mesh.duplicate_move.assert_called_with(
            MESH_OT_duplicate={},
            TRANSFORM_OT_translate={"value": (2, 0, 0)}
        )
        assert "moved by" in result
        assert "[2, 0, 0]" in result

    def test_duplicate_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no geometry selected."""
        with pytest.raises(ValueError, match="No geometry selected"):
            mesh_handler.duplicate_selected()

    def test_duplicate_reports_counts(self, mesh_handler, mock_edit_mode, mock_bmesh_with_faces):
        """Should report vertex, edge, and face counts."""
        bpy.ops.mesh.duplicate = MagicMock()

        result = mesh_handler.duplicate_selected()

        assert "vertices" in result
        assert "edges" in result
        assert "faces" in result
