"""
Tests for TASK-018 (Phase 2.5 - Advanced Precision) tools.
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
def mock_object_mode():
    """Sets up basic object mode mocks."""
    mock_obj = MagicMock()
    mock_obj.type = 'MESH'
    mock_obj.mode = 'OBJECT'
    mock_obj.data = MagicMock()
    mock_obj.data.polygons = [MagicMock() for _ in range(6)]  # 6 faces like a cube
    mock_obj.data.remesh_voxel_size = 0.1
    mock_obj.data.remesh_voxel_adaptivity = 0.0

    bpy.context.active_object = mock_obj
    bpy.ops.object.mode_set = MagicMock()
    bpy.ops.object.voxel_remesh = MagicMock()

    return mock_obj


@pytest.fixture
def mock_bmesh_with_verts():
    """Sets up bmesh with selected vertices."""
    mock_bm = MagicMock()
    mock_vert = MagicMock()
    mock_vert.select = True
    mock_vert.index = 0
    mock_bm.verts = [mock_vert]
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_bmesh_with_edges():
    """Sets up bmesh with selected edges."""
    mock_bm = MagicMock()
    mock_edge = MagicMock()
    mock_edge.select = True
    mock_bm.edges = [mock_edge]
    mock_bm.verts = []
    bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)
    return mock_bm


@pytest.fixture
def mock_bmesh_with_faces():
    """Sets up bmesh with selected faces."""
    mock_bm = MagicMock()
    mock_face = MagicMock()
    mock_face.select = True
    mock_face.verts = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]  # Quad
    mock_bm.faces = [mock_face]
    mock_bm.verts = [MagicMock(select=True)]
    mock_bm.edges = []
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


# =============================================================================
# TASK-018-1: mesh_bisect tests
# =============================================================================

class TestMeshBisect:
    """Tests for mesh_bisect tool."""

    def test_bisect_basic(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should bisect with basic parameters."""
        bpy.ops.mesh.bisect = MagicMock()

        result = mesh_handler.bisect(
            plane_co=[0, 0, 0],
            plane_no=[0, 0, 1]
        )

        bpy.ops.mesh.bisect.assert_called_with(
            plane_co=(0, 0, 0),
            plane_no=(0, 0, 1),
            clear_inner=False,
            clear_outer=False,
            use_fill=False
        )
        assert "Bisected" in result

    def test_bisect_with_clear_inner(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should bisect and clear inner geometry."""
        bpy.ops.mesh.bisect = MagicMock()

        result = mesh_handler.bisect(
            plane_co=[0, 0, 1],
            plane_no=[0, 0, 1],
            clear_inner=True
        )

        bpy.ops.mesh.bisect.assert_called_with(
            plane_co=(0, 0, 1),
            plane_no=(0, 0, 1),
            clear_inner=True,
            clear_outer=False,
            use_fill=False
        )
        assert "cleared inner" in result

    def test_bisect_with_fill(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should bisect and fill the cut."""
        bpy.ops.mesh.bisect = MagicMock()

        result = mesh_handler.bisect(
            plane_co=[0, 0, 0],
            plane_no=[1, 0, 0],
            fill=True
        )

        bpy.ops.mesh.bisect.assert_called_with(
            plane_co=(0, 0, 0),
            plane_no=(1, 0, 0),
            clear_inner=False,
            clear_outer=False,
            use_fill=True
        )
        assert "filled" in result

    def test_bisect_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no geometry selected."""
        with pytest.raises(ValueError, match="No geometry selected"):
            mesh_handler.bisect(plane_co=[0, 0, 0], plane_no=[0, 0, 1])

    def test_bisect_invalid_plane_co_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should raise ValueError for invalid plane_co."""
        with pytest.raises(ValueError, match="plane_co must be"):
            mesh_handler.bisect(plane_co=[0, 0], plane_no=[0, 0, 1])

    def test_bisect_invalid_plane_no_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should raise ValueError for invalid plane_no."""
        with pytest.raises(ValueError, match="plane_no must be"):
            mesh_handler.bisect(plane_co=[0, 0, 0], plane_no=[0, 1])


# =============================================================================
# TASK-018-2: mesh_edge_slide tests
# =============================================================================

class TestMeshEdgeSlide:
    """Tests for mesh_edge_slide tool."""

    def test_edge_slide_positive(self, mesh_handler, mock_edit_mode, mock_bmesh_with_edges):
        """Should slide edges with positive value."""
        bpy.ops.transform.edge_slide = MagicMock()

        result = mesh_handler.edge_slide(value=0.5)

        bpy.ops.transform.edge_slide.assert_called_with(value=0.5)
        assert "Slid" in result
        assert "edge" in result

    def test_edge_slide_negative(self, mesh_handler, mock_edit_mode, mock_bmesh_with_edges):
        """Should slide edges with negative value."""
        bpy.ops.transform.edge_slide = MagicMock()

        result = mesh_handler.edge_slide(value=-0.3)

        bpy.ops.transform.edge_slide.assert_called_with(value=-0.3)
        assert "Slid" in result

    def test_edge_slide_clamps_value(self, mesh_handler, mock_edit_mode, mock_bmesh_with_edges):
        """Should clamp value to [-1, 1] range."""
        bpy.ops.transform.edge_slide = MagicMock()

        mesh_handler.edge_slide(value=2.0)
        bpy.ops.transform.edge_slide.assert_called_with(value=1.0)

        mesh_handler.edge_slide(value=-2.0)
        bpy.ops.transform.edge_slide.assert_called_with(value=-1.0)

    def test_edge_slide_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no edges selected."""
        with pytest.raises(ValueError, match="No edges selected"):
            mesh_handler.edge_slide(value=0.5)


# =============================================================================
# TASK-018-2: mesh_vert_slide tests
# =============================================================================

class TestMeshVertSlide:
    """Tests for mesh_vert_slide tool."""

    def test_vert_slide_positive(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should slide vertices with positive value."""
        bpy.ops.transform.vert_slide = MagicMock()

        result = mesh_handler.vert_slide(value=0.5)

        bpy.ops.transform.vert_slide.assert_called_with(value=0.5)
        assert "Slid" in result
        assert "vertex" in result.lower()

    def test_vert_slide_negative(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should slide vertices with negative value."""
        bpy.ops.transform.vert_slide = MagicMock()

        result = mesh_handler.vert_slide(value=-0.2)

        bpy.ops.transform.vert_slide.assert_called_with(value=-0.2)
        assert "Slid" in result

    def test_vert_slide_clamps_value(self, mesh_handler, mock_edit_mode, mock_bmesh_with_verts):
        """Should clamp value to [-1, 1] range."""
        bpy.ops.transform.vert_slide = MagicMock()

        mesh_handler.vert_slide(value=1.5)
        bpy.ops.transform.vert_slide.assert_called_with(value=1.0)

        mesh_handler.vert_slide(value=-1.5)
        bpy.ops.transform.vert_slide.assert_called_with(value=-1.0)

    def test_vert_slide_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no vertices selected."""
        with pytest.raises(ValueError, match="No vertices selected"):
            mesh_handler.vert_slide(value=0.5)


# =============================================================================
# TASK-018-3: mesh_triangulate tests
# =============================================================================

class TestMeshTriangulate:
    """Tests for mesh_triangulate tool."""

    def test_triangulate_success(self, mesh_handler, mock_edit_mode, mock_bmesh_with_faces):
        """Should triangulate selected faces."""
        bpy.ops.mesh.quads_convert_to_tris = MagicMock()

        result = mesh_handler.triangulate()

        bpy.ops.mesh.quads_convert_to_tris.assert_called()
        assert "Triangulated" in result

    def test_triangulate_reports_non_triangular_count(self, mesh_handler, mock_edit_mode, mock_bmesh_with_faces):
        """Should report count of non-triangular faces."""
        bpy.ops.mesh.quads_convert_to_tris = MagicMock()

        result = mesh_handler.triangulate()

        # The mock face has 4 verts (quad), so it's non-triangular
        assert "1 were non-triangular" in result

    def test_triangulate_no_selection_raises(self, mesh_handler, mock_edit_mode, mock_bmesh_empty):
        """Should raise ValueError when no faces selected."""
        with pytest.raises(ValueError, match="No faces selected"):
            mesh_handler.triangulate()


# =============================================================================
# TASK-018-4: mesh_remesh_voxel tests
# =============================================================================

class TestMeshRemeshVoxel:
    """Tests for mesh_remesh_voxel tool."""

    def test_remesh_voxel_default(self, mesh_handler, mock_object_mode):
        """Should remesh with default parameters."""
        result = mesh_handler.remesh_voxel()

        assert mock_object_mode.data.remesh_voxel_size == 0.1
        assert mock_object_mode.data.remesh_voxel_adaptivity == 0.0
        bpy.ops.object.voxel_remesh.assert_called()
        assert "Voxel remesh complete" in result

    def test_remesh_voxel_custom_params(self, mesh_handler, mock_object_mode):
        """Should remesh with custom parameters."""
        result = mesh_handler.remesh_voxel(voxel_size=0.05, adaptivity=0.5)

        assert mock_object_mode.data.remesh_voxel_size == 0.05
        assert mock_object_mode.data.remesh_voxel_adaptivity == 0.5
        assert "voxel_size=0.05" in result
        assert "adaptivity=0.5" in result

    def test_remesh_voxel_reports_face_change(self, mesh_handler, mock_object_mode):
        """Should report face count change."""
        result = mesh_handler.remesh_voxel()

        assert "Faces:" in result
        assert "6" in result  # Original face count from mock

    def test_remesh_voxel_not_mesh_raises(self, mesh_handler):
        """Should raise ValueError when active object is not a mesh."""
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'CURVE'

        with pytest.raises(ValueError, match="Active object must be a Mesh"):
            mesh_handler.remesh_voxel()

    def test_remesh_voxel_no_active_raises(self, mesh_handler):
        """Should raise ValueError when no active object."""
        bpy.context.active_object = None

        with pytest.raises(ValueError, match="Active object must be a Mesh"):
            mesh_handler.remesh_voxel()
