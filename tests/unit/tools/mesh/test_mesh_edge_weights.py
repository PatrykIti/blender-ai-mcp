"""
Unit tests for TASK-029: Edge Weights & Creases (Subdivision Control)

Tests:
- mesh_edge_crease
- mesh_bevel_weight
- mesh_mark_sharp
"""

import unittest
from unittest.mock import MagicMock, PropertyMock
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
if 'bmesh' not in sys.modules:
    sys.modules['bmesh'] = MagicMock()

import bpy
import bmesh

from blender_addon.application.handlers.mesh import MeshHandler


class MockEdgeSequence:
    """Custom mock for BMesh edge sequence supporting both iteration and layers."""

    def __init__(self, edges):
        self._edges = edges
        self.layers = MagicMock()
        self.layers.crease = MagicMock()
        self.layers.bevel_weight = MagicMock()

    def __iter__(self):
        return iter(self._edges)

    def __len__(self):
        return len(self._edges)


class TestMeshEdgeCrease(unittest.TestCase):
    """Tests for mesh_edge_crease (TASK-029-1)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.object.mode_set = MagicMock()

        # Setup BMesh mock with custom edge sequence
        self.mock_bm = MagicMock()
        self.mock_edge1 = MagicMock()
        self.mock_edge1.select = True
        self.mock_edge2 = MagicMock()
        self.mock_edge2.select = True
        self.mock_edge3 = MagicMock()
        self.mock_edge3.select = False

        # Use custom MockEdgeSequence
        self.mock_edges = MockEdgeSequence([self.mock_edge1, self.mock_edge2, self.mock_edge3])
        self.mock_bm.edges = self.mock_edges

        # Mock crease layer
        self.mock_crease_layer = MagicMock()
        self.mock_edges.layers.crease.verify.return_value = self.mock_crease_layer

        bmesh.from_edit_mesh.return_value = self.mock_bm
        bmesh.update_edit_mesh = MagicMock()

    def test_edge_crease_full_sharp(self):
        """Test setting full crease (1.0) on selected edges"""
        result = self.handler.edge_crease(crease_value=1.0)

        # Verify BMesh was obtained
        bmesh.from_edit_mesh.assert_called()

        # Verify crease layer was verified/created
        self.mock_edges.layers.crease.verify.assert_called_once()

        # Verify mesh was updated
        bmesh.update_edit_mesh.assert_called()

        # Verify result message
        self.assertIn("2", result)  # 2 selected edges
        self.assertIn("1.0", result)

    def test_edge_crease_partial(self):
        """Test setting partial crease (0.5) on selected edges"""
        result = self.handler.edge_crease(crease_value=0.5)

        self.assertIn("0.5", result)

    def test_edge_crease_remove(self):
        """Test removing crease (0.0) from selected edges"""
        result = self.handler.edge_crease(crease_value=0.0)

        self.assertIn("0.0", result)

    def test_edge_crease_clamps_value(self):
        """Test that crease value is clamped to 0.0-1.0 range"""
        # Value above 1.0 should be clamped
        result = self.handler.edge_crease(crease_value=2.0)
        self.assertIn("1.0", result)

        # Value below 0.0 should be clamped
        result = self.handler.edge_crease(crease_value=-0.5)
        self.assertIn("0.0", result)

    def test_edge_crease_no_selection_raises(self):
        """Test that error is raised when no edges selected"""
        # Setup: no selected edges
        self.mock_edge1.select = False
        self.mock_edge2.select = False

        with self.assertRaises(ValueError) as context:
            self.handler.edge_crease(crease_value=1.0)

        self.assertIn("No edges selected", str(context.exception))


class TestMeshBevelWeight(unittest.TestCase):
    """Tests for mesh_bevel_weight (TASK-029-2)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.object.mode_set = MagicMock()

        # Setup BMesh mock
        self.mock_bm = MagicMock()
        self.mock_edge1 = MagicMock()
        self.mock_edge1.select = True
        self.mock_edge2 = MagicMock()
        self.mock_edge2.select = False

        # Use custom MockEdgeSequence
        self.mock_edges = MockEdgeSequence([self.mock_edge1, self.mock_edge2])
        self.mock_bm.edges = self.mock_edges

        # Mock bevel weight layer
        self.mock_bevel_layer = MagicMock()
        self.mock_edges.layers.bevel_weight.verify.return_value = self.mock_bevel_layer

        bmesh.from_edit_mesh.return_value = self.mock_bm
        bmesh.update_edit_mesh = MagicMock()

    def test_bevel_weight_full(self):
        """Test setting full bevel weight (1.0) on selected edges"""
        result = self.handler.bevel_weight(weight=1.0)

        # Verify bevel weight layer was verified/created
        self.mock_edges.layers.bevel_weight.verify.assert_called_once()

        # Verify mesh was updated
        bmesh.update_edit_mesh.assert_called()

        # Verify result message
        self.assertIn("1", result)  # 1 selected edge
        self.assertIn("1.0", result)

    def test_bevel_weight_partial(self):
        """Test setting partial bevel weight (0.5)"""
        result = self.handler.bevel_weight(weight=0.5)

        self.assertIn("0.5", result)

    def test_bevel_weight_remove(self):
        """Test removing bevel weight (0.0)"""
        result = self.handler.bevel_weight(weight=0.0)

        self.assertIn("0.0", result)

    def test_bevel_weight_clamps_value(self):
        """Test that bevel weight is clamped to 0.0-1.0 range"""
        result = self.handler.bevel_weight(weight=1.5)
        self.assertIn("1.0", result)

        result = self.handler.bevel_weight(weight=-0.3)
        self.assertIn("0.0", result)

    def test_bevel_weight_no_selection_raises(self):
        """Test that error is raised when no edges selected"""
        self.mock_edge1.select = False

        with self.assertRaises(ValueError) as context:
            self.handler.bevel_weight(weight=1.0)

        self.assertIn("No edges selected", str(context.exception))


class TestMeshMarkSharp(unittest.TestCase):
    """Tests for mesh_mark_sharp (TASK-029-3)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.mark_sharp = MagicMock()

        # Setup BMesh mock
        self.mock_bm = MagicMock()
        self.mock_edge1 = MagicMock()
        self.mock_edge1.select = True
        self.mock_edge2 = MagicMock()
        self.mock_edge2.select = True
        self.mock_edge3 = MagicMock()
        self.mock_edge3.select = False

        self.mock_bm.edges = [self.mock_edge1, self.mock_edge2, self.mock_edge3]

        bmesh.from_edit_mesh.return_value = self.mock_bm

    def test_mark_sharp(self):
        """Test marking edges as sharp"""
        result = self.handler.mark_sharp(action="mark")

        # Verify mark_sharp was called without clear
        bpy.ops.mesh.mark_sharp.assert_called_once_with()

        # Verify result message
        self.assertIn("Marked", result)
        self.assertIn("2", result)  # 2 selected edges

    def test_clear_sharp(self):
        """Test clearing sharp from edges"""
        result = self.handler.mark_sharp(action="clear")

        # Verify mark_sharp was called with clear=True
        bpy.ops.mesh.mark_sharp.assert_called_once_with(clear=True)

        # Verify result message
        self.assertIn("Cleared", result)
        self.assertIn("2", result)

    def test_mark_sharp_case_insensitive(self):
        """Test that action is case-insensitive"""
        result = self.handler.mark_sharp(action="MARK")
        self.assertIn("Marked", result)

        bpy.ops.mesh.mark_sharp.reset_mock()

        result = self.handler.mark_sharp(action="CLEAR")
        self.assertIn("Cleared", result)

    def test_mark_sharp_invalid_action_raises(self):
        """Test that invalid action raises error"""
        with self.assertRaises(ValueError) as context:
            self.handler.mark_sharp(action="invalid")

        self.assertIn("Invalid action", str(context.exception))

    def test_mark_sharp_no_selection_raises(self):
        """Test that error is raised when no edges selected"""
        self.mock_edge1.select = False
        self.mock_edge2.select = False

        with self.assertRaises(ValueError) as context:
            self.handler.mark_sharp(action="mark")

        self.assertIn("No edges selected", str(context.exception))


if __name__ == '__main__':
    unittest.main()
