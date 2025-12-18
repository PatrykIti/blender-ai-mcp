"""
Unit tests for TASK-036: Symmetry & Advanced Fill

Tests:
- mesh_symmetrize
- mesh_grid_fill
- mesh_poke_faces
- mesh_beautify_fill
- mesh_mirror
"""

import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
if 'bmesh' not in sys.modules:
    sys.modules['bmesh'] = MagicMock()

import bpy
import bmesh

from blender_addon.application.handlers.mesh import MeshHandler


def create_mock_bmesh_with_selection(verts=10, edges=15, faces=6):
    """Create a mock bmesh with selected elements."""
    mock_bm = MagicMock()

    # Mock vertices
    mock_verts = [MagicMock(select=True) for _ in range(verts)]
    mock_bm.verts = mock_verts

    # Mock edges
    mock_edges = [MagicMock(select=True) for _ in range(edges)]
    mock_bm.edges = mock_edges

    # Mock faces
    mock_faces = [MagicMock(select=True) for _ in range(faces)]
    mock_bm.faces = mock_faces

    return mock_bm


class TestMeshSymmetrize(unittest.TestCase):
    """Tests for mesh_symmetrize (TASK-036-1)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.context.active_object.data = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.symmetrize = MagicMock()

    def test_symmetrize_default(self):
        """Test symmetrize with default parameters"""
        result = self.handler.symmetrize()

        bpy.ops.mesh.symmetrize.assert_called_once()
        self.assertIn("Symmetrized", result)
        self.assertIn("NEGATIVE_X", result)

    def test_symmetrize_positive_x(self):
        """Test symmetrize with POSITIVE_X direction"""
        result = self.handler.symmetrize(direction="POSITIVE_X")

        bpy.ops.mesh.symmetrize.assert_called_once()
        self.assertIn("POSITIVE_X", result)

    def test_symmetrize_y_axis(self):
        """Test symmetrize on Y axis"""
        result = self.handler.symmetrize(direction="NEGATIVE_Y")

        bpy.ops.mesh.symmetrize.assert_called_once()
        self.assertIn("NEGATIVE_Y", result)

    def test_symmetrize_z_axis(self):
        """Test symmetrize on Z axis"""
        result = self.handler.symmetrize(direction="POSITIVE_Z")

        bpy.ops.mesh.symmetrize.assert_called_once()
        self.assertIn("POSITIVE_Z", result)

    def test_symmetrize_custom_threshold(self):
        """Test symmetrize with custom threshold"""
        result = self.handler.symmetrize(threshold=0.001)

        bpy.ops.mesh.symmetrize.assert_called_once()
        self.assertIn("0.001", result)

    def test_symmetrize_case_insensitive(self):
        """Test that direction is case-insensitive"""
        result = self.handler.symmetrize(direction="negative_x")
        self.assertIn("NEGATIVE_X", result)

    def test_symmetrize_invalid_direction_raises(self):
        """Test that invalid direction raises error"""
        with self.assertRaises(ValueError) as context:
            self.handler.symmetrize(direction="INVALID")

        self.assertIn("Invalid direction", str(context.exception))

    def test_symmetrize_runtime_error(self):
        """Test symmetrize handles runtime error"""
        bpy.ops.mesh.symmetrize.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.symmetrize()

        self.assertIn("Symmetrize failed", str(context.exception))


class TestMeshGridFill(unittest.TestCase):
    """Tests for mesh_grid_fill (TASK-036-2)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.context.active_object.data = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.fill_grid = MagicMock()

        # Mock bmesh with selected edges
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(edges=10))

    def test_grid_fill_default(self):
        """Test grid fill with default parameters"""
        result = self.handler.grid_fill()

        bpy.ops.mesh.fill_grid.assert_called_once_with(
            span=1,
            offset=0,
            use_interp_simple=False
        )
        self.assertIn("Grid fill", result)

    def test_grid_fill_custom_span(self):
        """Test grid fill with custom span"""
        result = self.handler.grid_fill(span=4)

        bpy.ops.mesh.fill_grid.assert_called_once_with(
            span=4,
            offset=0,
            use_interp_simple=False
        )
        self.assertIn("span=4", result)

    def test_grid_fill_custom_offset(self):
        """Test grid fill with custom offset"""
        result = self.handler.grid_fill(offset=2)

        bpy.ops.mesh.fill_grid.assert_called_once_with(
            span=1,
            offset=2,
            use_interp_simple=False
        )
        self.assertIn("offset=2", result)

    def test_grid_fill_simple_interpolation(self):
        """Test grid fill with simple interpolation"""
        result = self.handler.grid_fill(use_interp_simple=True)

        bpy.ops.mesh.fill_grid.assert_called_once_with(
            span=1,
            offset=0,
            use_interp_simple=True
        )

    def test_grid_fill_all_parameters(self):
        """Test grid fill with all parameters"""
        result = self.handler.grid_fill(span=3, offset=1, use_interp_simple=True)

        bpy.ops.mesh.fill_grid.assert_called_once_with(
            span=3,
            offset=1,
            use_interp_simple=True
        )

    def test_grid_fill_no_selection_raises(self):
        """Test grid fill raises error when no edges selected"""
        # Mock bmesh with no selected edges
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(edges=0))

        with self.assertRaises(ValueError) as context:
            self.handler.grid_fill()

        self.assertIn("Select at least 3 edges", str(context.exception))

    def test_grid_fill_runtime_error(self):
        """Test grid fill handles runtime error"""
        bpy.ops.mesh.fill_grid.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.grid_fill()

        self.assertIn("Grid fill failed", str(context.exception))


class TestMeshPokeFaces(unittest.TestCase):
    """Tests for mesh_poke_faces (TASK-036-3)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.context.active_object.data = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.poke = MagicMock()

        # Mock bmesh with selected faces
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(faces=6))

    def test_poke_faces_default(self):
        """Test poke faces with default parameters"""
        result = self.handler.poke_faces()

        bpy.ops.mesh.poke.assert_called_once_with(
            offset=0.0,
            use_relative_offset=False,
            center_mode='MEDIAN_WEIGHTED'
        )
        self.assertIn("Poked", result)

    def test_poke_faces_with_offset(self):
        """Test poke faces with custom offset"""
        result = self.handler.poke_faces(offset=0.5)

        bpy.ops.mesh.poke.assert_called_once_with(
            offset=0.5,
            use_relative_offset=False,
            center_mode='MEDIAN_WEIGHTED'
        )
        self.assertIn("offset=0.5", result)

    def test_poke_faces_relative_offset(self):
        """Test poke faces with relative offset"""
        result = self.handler.poke_faces(offset=0.3, use_relative_offset=True)

        bpy.ops.mesh.poke.assert_called_once_with(
            offset=0.3,
            use_relative_offset=True,
            center_mode='MEDIAN_WEIGHTED'
        )

    def test_poke_faces_center_mode_median(self):
        """Test poke faces with MEDIAN center mode"""
        result = self.handler.poke_faces(center_mode="MEDIAN")

        bpy.ops.mesh.poke.assert_called_once_with(
            offset=0.0,
            use_relative_offset=False,
            center_mode='MEDIAN'
        )
        self.assertIn("MEDIAN", result)

    def test_poke_faces_center_mode_bounds(self):
        """Test poke faces with BOUNDS center mode"""
        result = self.handler.poke_faces(center_mode="BOUNDS")

        bpy.ops.mesh.poke.assert_called_once_with(
            offset=0.0,
            use_relative_offset=False,
            center_mode='BOUNDS'
        )
        self.assertIn("BOUNDS", result)

    def test_poke_faces_case_insensitive(self):
        """Test that center_mode is case-insensitive"""
        result = self.handler.poke_faces(center_mode="median_weighted")
        self.assertIn("MEDIAN_WEIGHTED", result)

    def test_poke_faces_invalid_center_mode_raises(self):
        """Test that invalid center_mode raises error"""
        with self.assertRaises(ValueError) as context:
            self.handler.poke_faces(center_mode="INVALID")

        self.assertIn("Invalid center_mode", str(context.exception))

    def test_poke_faces_no_selection_raises(self):
        """Test poke faces raises error when no faces selected"""
        # Mock bmesh with no selected faces
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(faces=0))

        with self.assertRaises(ValueError) as context:
            self.handler.poke_faces()

        self.assertIn("No faces selected", str(context.exception))

    def test_poke_faces_runtime_error(self):
        """Test poke faces handles runtime error"""
        bpy.ops.mesh.poke.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.poke_faces()

        self.assertIn("Poke faces failed", str(context.exception))


class TestMeshBeautifyFill(unittest.TestCase):
    """Tests for mesh_beautify_fill (TASK-036-4)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.context.active_object.data = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.beautify_fill = MagicMock()

        # Mock bmesh with selected faces
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(faces=6))

    def test_beautify_fill_default(self):
        """Test beautify fill with default angle limit"""
        result = self.handler.beautify_fill()

        bpy.ops.mesh.beautify_fill.assert_called_once()
        self.assertIn("Beautif", result)
        self.assertIn("180.0", result)

    def test_beautify_fill_custom_angle(self):
        """Test beautify fill with custom angle limit"""
        result = self.handler.beautify_fill(angle_limit=90.0)

        bpy.ops.mesh.beautify_fill.assert_called_once()
        self.assertIn("90.0", result)

    def test_beautify_fill_small_angle(self):
        """Test beautify fill with small angle limit"""
        result = self.handler.beautify_fill(angle_limit=45.0)

        self.assertIn("45.0", result)

    def test_beautify_fill_no_selection_raises(self):
        """Test beautify fill raises error when no faces selected"""
        # Mock bmesh with no selected faces
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(faces=0))

        with self.assertRaises(ValueError) as context:
            self.handler.beautify_fill()

        self.assertIn("No faces selected", str(context.exception))

    def test_beautify_fill_runtime_error(self):
        """Test beautify fill handles runtime error"""
        bpy.ops.mesh.beautify_fill.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.beautify_fill()

        self.assertIn("Beautify fill failed", str(context.exception))


class TestMeshMirror(unittest.TestCase):
    """Tests for mesh_mirror (TASK-036-5)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.context.active_object.data = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.transform.mirror = MagicMock()
        bpy.ops.mesh.remove_doubles = MagicMock()

        # Mock bmesh with selected verts
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(verts=8))

    def test_mirror_default(self):
        """Test mirror with default parameters (X axis)"""
        result = self.handler.mirror()

        bpy.ops.transform.mirror.assert_called_once()
        self.assertIn("Mirrored", result)
        self.assertIn("X", result)

    def test_mirror_y_axis(self):
        """Test mirror on Y axis"""
        result = self.handler.mirror(axis="Y")

        bpy.ops.transform.mirror.assert_called_once()
        self.assertIn("Y", result)

    def test_mirror_z_axis(self):
        """Test mirror on Z axis"""
        result = self.handler.mirror(axis="Z")

        bpy.ops.transform.mirror.assert_called_once()
        self.assertIn("Z", result)

    def test_mirror_with_merge(self):
        """Test mirror with merge enabled (default)"""
        result = self.handler.mirror(use_mirror_merge=True)

        bpy.ops.transform.mirror.assert_called_once()
        bpy.ops.mesh.remove_doubles.assert_called_once()
        self.assertIn("merged", result.lower())

    def test_mirror_without_merge(self):
        """Test mirror without merge"""
        result = self.handler.mirror(use_mirror_merge=False)

        bpy.ops.transform.mirror.assert_called_once()
        bpy.ops.mesh.remove_doubles.assert_not_called()

    def test_mirror_custom_threshold(self):
        """Test mirror with custom merge threshold"""
        result = self.handler.mirror(merge_threshold=0.01)

        bpy.ops.mesh.remove_doubles.assert_called_once_with(threshold=0.01)
        self.assertIn("0.01", result)

    def test_mirror_case_insensitive(self):
        """Test that axis is case-insensitive"""
        result = self.handler.mirror(axis="x")
        self.assertIn("X", result)

    def test_mirror_invalid_axis_raises(self):
        """Test that invalid axis raises error"""
        with self.assertRaises(ValueError) as context:
            self.handler.mirror(axis="W")

        self.assertIn("Invalid axis", str(context.exception))

    def test_mirror_no_selection_raises(self):
        """Test mirror raises error when no vertices selected"""
        # Mock bmesh with no selected verts
        bmesh.from_edit_mesh = MagicMock(return_value=create_mock_bmesh_with_selection(verts=0))

        with self.assertRaises(ValueError) as context:
            self.handler.mirror()

        self.assertIn("No geometry selected", str(context.exception))

    def test_mirror_runtime_error(self):
        """Test mirror handles runtime error"""
        bpy.ops.transform.mirror.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.mirror()

        self.assertIn("Mirror failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()
