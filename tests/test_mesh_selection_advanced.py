"""Tests for advanced mesh selection tools (Phase 2.1)."""
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

class TestMeshSelectLoop(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'OBJECT'
        bpy.context.mode = 'OBJECT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.loop_multi_select = MagicMock()
        bmesh.from_edit_mesh = MagicMock()
        bmesh.update_edit_mesh = MagicMock()

    def test_select_loop_basic(self):
        """Should select edge loop from target edge."""
        # Setup BMesh mock
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create 10 edges
        edges = []
        for i in range(10):
            edge = MagicMock()
            edge.select = False
            edge.index = i
            edges.append(edge)

        # Mock sequence behavior for bm.edges
        mock_edges_seq = MagicMock()
        mock_edges_seq.__iter__.return_value = iter(edges)
        mock_edges_seq.__len__.return_value = len(edges)
        mock_edges_seq.__getitem__.side_effect = lambda idx: edges[idx]
        bm.edges = mock_edges_seq

        # Mock verts and faces
        bm.verts = MagicMock()
        bm.verts.__iter__.return_value = iter([])
        bm.faces = MagicMock()
        bm.faces.__iter__.return_value = iter([])

        # Execute
        result = self.handler.select_loop(edge_index=5)

        # Verify
        bpy.ops.object.mode_set.assert_any_call(mode='EDIT')
        assert edges[5].select == True, "Target edge should be selected"
        bpy.ops.mesh.loop_multi_select.assert_called_once_with(ring=False)
        assert "Selected edge loop from edge 5" in result

    def test_select_loop_invalid_index(self):
        """Should raise ValueError for invalid edge index."""
        # Setup BMesh mock
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create 5 edges
        edges = [MagicMock() for _ in range(5)]
        mock_edges_seq = MagicMock()
        mock_edges_seq.__len__.return_value = len(edges)
        bm.edges = mock_edges_seq

        bm.verts = MagicMock()
        bm.verts.__iter__.return_value = iter([])
        bm.faces = MagicMock()
        bm.faces.__iter__.return_value = iter([])

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            self.handler.select_loop(edge_index=10)

        assert "Invalid edge_index 10" in str(context.exception)
        assert "Mesh has 5 edges" in str(context.exception)

    def test_select_loop_restores_mode(self):
        """Should restore previous mode after selection."""
        # Setup: Start in OBJECT mode
        bpy.context.active_object.mode = 'OBJECT'
        bpy.context.object = bpy.context.active_object

        # Setup BMesh mock
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        edges = [MagicMock() for _ in range(5)]
        mock_edges_seq = MagicMock()
        mock_edges_seq.__iter__.return_value = iter(edges)
        mock_edges_seq.__len__.return_value = len(edges)
        mock_edges_seq.__getitem__.side_effect = lambda idx: edges[idx]
        bm.edges = mock_edges_seq

        bm.verts = MagicMock()
        bm.verts.__iter__.return_value = iter([])
        bm.faces = MagicMock()
        bm.faces.__iter__.return_value = iter([])

        # Execute
        self.handler.select_loop(edge_index=2)

        # Verify mode restoration
        mode_set_calls = [call[1]['mode'] for call in bpy.ops.object.mode_set.call_args_list]
        assert 'EDIT' in mode_set_calls, "Should switch to EDIT mode"
        assert 'OBJECT' in mode_set_calls, "Should restore OBJECT mode"


if __name__ == '__main__':
    unittest.main()
