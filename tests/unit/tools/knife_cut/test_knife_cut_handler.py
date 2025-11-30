"""
Unit tests for TASK-032: Knife & Cut Tools

Tests:
- mesh_knife_project
- mesh_rip
- mesh_split
- mesh_edge_split
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


def create_mock_collection(items):
    """Creates a MagicMock that behaves like a list for iteration."""
    mock = MagicMock()
    mock.__iter__ = MagicMock(return_value=iter(items))
    return mock


class TestMeshKnifeProject(unittest.TestCase):
    """Tests for mesh_knife_project (TASK-032-1)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.mesh.knife_project = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        # Mock bmesh
        mock_bm = MagicMock()
        mock_bm.faces = create_mock_collection([MagicMock(select=True)])
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

    def test_knife_project_cut_through(self):
        """Test knife project with cut_through=True (default)"""
        result = self.handler.knife_project(cut_through=True)

        bpy.ops.mesh.knife_project.assert_called_once_with(cut_through=True)
        self.assertIn("Knife project completed", result)
        self.assertIn("through entire mesh", result)

    def test_knife_project_visible_only(self):
        """Test knife project with cut_through=False"""
        result = self.handler.knife_project(cut_through=False)

        bpy.ops.mesh.knife_project.assert_called_once_with(cut_through=False)
        self.assertIn("Knife project completed", result)
        self.assertIn("visible faces only", result)


class TestMeshRip(unittest.TestCase):
    """Tests for mesh_rip (TASK-032-2)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.mesh.rip_move = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        # Mock screen areas for temp_override context
        mock_region = MagicMock()
        mock_region.type = 'WINDOW'

        mock_area = MagicMock()
        mock_area.type = 'VIEW_3D'
        mock_area.regions = [mock_region]

        bpy.context.screen = MagicMock()
        bpy.context.screen.areas = [mock_area]

        # Mock temp_override context manager
        bpy.context.temp_override = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))

        # Mock bmesh with selected vertices
        mock_bm = MagicMock()
        mock_verts = [MagicMock(select=True), MagicMock(select=True)]
        mock_bm.verts = create_mock_collection(mock_verts)
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

    def test_rip_default(self):
        """Test rip with default parameters"""
        result = self.handler.rip()

        # The rip_move is called inside temp_override context
        bpy.ops.mesh.rip_move.assert_called_once()
        self.assertIn("Ripped", result)
        self.assertIn("vertex", result)

    def test_rip_with_fill(self):
        """Test rip with use_fill=True"""
        result = self.handler.rip(use_fill=True)

        bpy.ops.mesh.rip_move.assert_called_once()
        self.assertIn("hole filled", result)

    def test_rip_no_selection_raises(self):
        """Test that rip without selection raises error"""
        # Mock empty selection
        mock_bm = MagicMock()
        mock_verts = [MagicMock(select=False), MagicMock(select=False)]
        mock_bm.verts = create_mock_collection(mock_verts)
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

        with self.assertRaises(ValueError) as context:
            self.handler.rip()

        self.assertIn("No vertices selected", str(context.exception))


class TestMeshSplit(unittest.TestCase):
    """Tests for mesh_split (TASK-032-3)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.mesh.split = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        # Mock bmesh with selection
        mock_bm = MagicMock()
        mock_verts = [MagicMock(select=True), MagicMock(select=True), MagicMock(select=True)]
        mock_faces = [MagicMock(select=True)]
        mock_bm.verts = create_mock_collection(mock_verts)
        mock_bm.faces = create_mock_collection(mock_faces)
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

    def test_split_default(self):
        """Test split selected geometry"""
        result = self.handler.split()

        bpy.ops.mesh.split.assert_called_once()
        self.assertIn("Split", result)
        self.assertIn("vertices", result)
        self.assertIn("faces", result)

    def test_split_no_selection_raises(self):
        """Test that split without selection raises error"""
        # Mock empty selection
        mock_bm = MagicMock()
        mock_verts = [MagicMock(select=False), MagicMock(select=False)]
        mock_faces = [MagicMock(select=False)]
        mock_bm.verts = create_mock_collection(mock_verts)
        mock_bm.faces = create_mock_collection(mock_faces)
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

        with self.assertRaises(ValueError) as context:
            self.handler.split()

        self.assertIn("No geometry selected", str(context.exception))


class TestMeshEdgeSplit(unittest.TestCase):
    """Tests for mesh_edge_split (TASK-032-4)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.mesh.edge_split = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        # Mock bmesh with selected edges
        mock_bm = MagicMock()
        mock_edges = [MagicMock(select=True), MagicMock(select=True)]
        mock_bm.edges = create_mock_collection(mock_edges)
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

    def test_edge_split_default(self):
        """Test edge split with selected edges"""
        result = self.handler.edge_split()

        bpy.ops.mesh.edge_split.assert_called_once()
        self.assertIn("Split mesh at", result)
        self.assertIn("edge", result)

    def test_edge_split_no_selection_raises(self):
        """Test that edge_split without selection raises error"""
        # Mock empty selection
        mock_bm = MagicMock()
        mock_edges = [MagicMock(select=False), MagicMock(select=False)]
        mock_bm.edges = create_mock_collection(mock_edges)
        bmesh.from_edit_mesh = MagicMock(return_value=mock_bm)

        with self.assertRaises(ValueError) as context:
            self.handler.edge_split()

        self.assertIn("No edges selected", str(context.exception))


if __name__ == '__main__':
    unittest.main()
