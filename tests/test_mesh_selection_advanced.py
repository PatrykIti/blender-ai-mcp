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


class TestMeshSelectRing(unittest.TestCase):
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

    def test_select_ring_basic(self):
        """Should select edge ring from target edge."""
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
        result = self.handler.select_ring(edge_index=3)

        # Verify
        bpy.ops.object.mode_set.assert_any_call(mode='EDIT')
        assert edges[3].select == True, "Target edge should be selected"
        bpy.ops.mesh.loop_multi_select.assert_called_once_with(ring=True)
        assert "Selected edge ring from edge 3" in result

    def test_select_ring_invalid_index(self):
        """Should raise ValueError for invalid edge index."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        edges = [MagicMock() for _ in range(5)]
        mock_edges_seq = MagicMock()
        mock_edges_seq.__len__.return_value = len(edges)
        bm.edges = mock_edges_seq

        bm.verts = MagicMock()
        bm.verts.__iter__.return_value = iter([])
        bm.faces = MagicMock()
        bm.faces.__iter__.return_value = iter([])

        with self.assertRaises(ValueError) as context:
            self.handler.select_ring(edge_index=10)

        assert "Invalid edge_index 10" in str(context.exception)


class TestMeshSelectLinked(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'OBJECT'
        bpy.context.mode = 'OBJECT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.select_linked = MagicMock()
        bmesh.from_edit_mesh = MagicMock()
        bmesh.update_edit_mesh = MagicMock()

    def test_select_linked_basic(self):
        """Should select all linked geometry from current selection."""
        # Setup BMesh mock
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create verts - 3 selected initially
        verts = []
        for i in range(8):
            vert = MagicMock()
            vert.select = (i < 3)  # First 3 selected initially
            verts.append(vert)

        # Mock the selection behavior: after select_linked is called, all become selected
        def mock_select_linked():
            for v in verts:
                v.select = True

        bpy.ops.mesh.select_linked = mock_select_linked

        mock_verts_seq = MagicMock()
        # First __iter__ is for checking selected_count, second is for final_count (after operation)
        mock_verts_seq.__iter__.side_effect = [iter(verts), iter(verts)]
        bm.verts = mock_verts_seq

        # Execute
        result = self.handler.select_linked()

        # Verify
        bpy.ops.object.mode_set.assert_any_call(mode='EDIT')
        assert "Selected linked geometry" in result
        assert "8 vertices total" in result

    def test_select_linked_no_selection(self):
        """Should raise ValueError when nothing is selected."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # All verts unselected
        verts = [MagicMock() for _ in range(5)]
        for v in verts:
            v.select = False

        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.return_value = iter(verts)
        bm.verts = mock_verts_seq

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            self.handler.select_linked()

        assert "No geometry selected" in str(context.exception)
        bpy.ops.mesh.select_linked.assert_not_called()


if __name__ == '__main__':
    unittest.main()


class TestMeshSelectMoreLess(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'OBJECT'
        bpy.context.mode = 'OBJECT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.select_more = MagicMock()
        bpy.ops.mesh.select_less = MagicMock()
        bmesh.from_edit_mesh = MagicMock()
        bmesh.update_edit_mesh = MagicMock()

    def test_select_more_basic(self):
        """Should grow selection by one step."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create verts - 3 selected initially
        verts = []
        for i in range(10):
            vert = MagicMock()
            vert.select = (i < 3)
            verts.append(vert)

        # Mock grow behavior: 3 -> 6 verts selected
        def mock_select_more():
            for i in range(6):
                verts[i].select = True

        bpy.ops.mesh.select_more = mock_select_more

        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.side_effect = [iter(verts), iter(verts)]
        bm.verts = mock_verts_seq

        # Execute
        result = self.handler.select_more()

        # Verify
        assert "Grew selection" in result
        assert "3 -> 6 vertices" in result

    def test_select_less_basic(self):
        """Should shrink selection by one step."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create verts - 6 selected initially
        verts = []
        for i in range(10):
            vert = MagicMock()
            vert.select = (i < 6)
            verts.append(vert)

        # Mock shrink behavior: 6 -> 3 verts selected
        def mock_select_less():
            for i in range(3, 6):
                verts[i].select = False

        bpy.ops.mesh.select_less = mock_select_less

        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.side_effect = [iter(verts), iter(verts)]
        bm.verts = mock_verts_seq

        # Execute
        result = self.handler.select_less()

        # Verify
        assert "Shrunk selection" in result
        assert "6 -> 3 vertices" in result

    def test_select_more_no_selection(self):
        """Should raise ValueError when nothing is selected."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        verts = [MagicMock() for _ in range(5)]
        for v in verts:
            v.select = False

        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.return_value = iter(verts)
        bm.verts = mock_verts_seq

        with self.assertRaises(ValueError) as context:
            self.handler.select_more()

        assert "No geometry selected" in str(context.exception)


class TestMeshSelectByLocation(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'OBJECT'
        bpy.context.mode = 'OBJECT'
        bpy.ops.object.mode_set = MagicMock()
        bmesh.from_edit_mesh = MagicMock()
        bmesh.update_edit_mesh = MagicMock()

    def test_select_by_location_vertices(self):
        """Should select vertices within coordinate range."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create 10 vertices with Z coordinates from 0 to 9
        verts = []
        for i in range(10):
            v = MagicMock()
            v.co = MagicMock()
            v.co.__getitem__ = lambda self, idx, val=i: float(val) if idx == 2 else 0.0
            v.select = False
            verts.append(v)

        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.side_effect = [iter(verts), iter(verts)]
        bm.verts = mock_verts_seq

        bm.edges = MagicMock()
        bm.edges.__iter__.return_value = iter([])
        bm.faces = MagicMock()
        bm.faces.__iter__.return_value = iter([])

        # Execute: select vertices with Z between 3 and 6
        result = self.handler.select_by_location(axis='Z', min_coord=3.0, max_coord=6.0, mode='VERT')

        # Verify
        assert "Selected 4 vert(s)" in result  # Verts 3, 4, 5, 6
        assert "Z=[3.0, 6.0]" in result

    def test_select_by_location_invalid_axis(self):
        """Should raise ValueError for invalid axis."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        
        bm.verts = []
        bm.edges = []
        bm.faces = []

        with self.assertRaises(ValueError) as context:
            self.handler.select_by_location(axis='W', min_coord=0, max_coord=1)

        assert "Invalid axis 'W'" in str(context.exception)

    def test_select_by_location_invalid_mode(self):
        """Should raise ValueError for invalid mode."""
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        
        bm.verts = []
        bm.edges = []
        bm.faces = []

        with self.assertRaises(ValueError) as context:
            self.handler.select_by_location(axis='X', min_coord=0, max_coord=1, mode='INVALID')

        assert "Invalid mode 'INVALID'" in str(context.exception)
