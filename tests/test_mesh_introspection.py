"""Tests for mesh introspection tools (read-only data retrieval)."""
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

class TestMeshGetVertexData(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.view_layer = MagicMock()
        bpy.context.view_layer.objects.active = None
        bpy.data.objects = {}
        bpy.ops.object.mode_set = MagicMock()
        bmesh.from_edit_mesh = MagicMock()

    def test_get_vertex_data_all_vertices(self):
        """Should return data for all vertices."""
        # Setup object
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'
        obj.data = MagicMock()
        bpy.data.objects = {"Cube": obj}

        # Setup BMesh mock
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create 4 vertices - 2 selected, 2 not
        verts = []
        for i in range(4):
            v = MagicMock()
            v.index = i
            v.co = MagicMock()
            v.co.x = float(i)
            v.co.y = float(i * 2)
            v.co.z = float(i * 3)
            v.select = (i < 2)
            verts.append(v)

        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.return_value = iter(verts)
        mock_verts_seq.__len__.return_value = 4
        bm.verts = mock_verts_seq

        # Execute
        result = self.handler.get_vertex_data("Cube", selected_only=False)

        # Verify
        assert result["object_name"] == "Cube"
        assert result["vertex_count"] == 4
        assert result["selected_count"] == 2
        assert result["returned_count"] == 4
        assert len(result["vertices"]) == 4
        assert result["vertices"][0]["index"] == 0
        assert result["vertices"][0]["selected"] == True
        assert result["vertices"][2]["selected"] == False

    def test_get_vertex_data_selected_only(self):
        """Should return data only for selected vertices."""
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'
        obj.data = MagicMock()
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        # Create 4 vertices - 2 selected
        verts = []
        for i in range(4):
            v = MagicMock()
            v.index = i
            v.co = MagicMock()
            v.co.x = float(i)
            v.co.y = 0.0
            v.co.z = 0.0
            v.select = (i < 2)
            verts.append(v)

        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.return_value = iter(verts)
        mock_verts_seq.__len__.return_value = 4
        bm.verts = mock_verts_seq

        # Execute
        result = self.handler.get_vertex_data("Cube", selected_only=True)

        # Verify
        assert result["vertex_count"] == 4  # Total in mesh
        assert result["selected_count"] == 2
        assert result["returned_count"] == 2  # Only selected returned
        assert len(result["vertices"]) == 2
        assert all(v["selected"] for v in result["vertices"])

    def test_get_vertex_data_object_not_found(self):
        """Should raise ValueError when object doesn't exist."""
        bpy.data.objects = {}

        with self.assertRaises(ValueError) as context:
            self.handler.get_vertex_data("NonExistent")

        assert "Object 'NonExistent' not found" in str(context.exception)

    def test_get_vertex_data_not_mesh(self):
        """Should raise ValueError when object is not a mesh."""
        obj = MagicMock()
        obj.type = 'CAMERA'
        bpy.data.objects = {"Camera": obj}

        with self.assertRaises(ValueError) as context:
            self.handler.get_vertex_data("Camera")

        assert "is not a MESH" in str(context.exception)

    def test_get_vertex_data_restores_mode(self):
        """Should restore previous mode after reading data."""
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'
        obj.data = MagicMock()
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        
        mock_verts_seq = MagicMock()
        mock_verts_seq.__iter__.return_value = iter([])
        mock_verts_seq.__len__.return_value = 0
        bm.verts = mock_verts_seq

        # Execute
        self.handler.get_vertex_data("Cube")

        # Verify mode was switched to EDIT and back to OBJECT
        mode_calls = [call[1]['mode'] for call in bpy.ops.object.mode_set.call_args_list]
        assert 'EDIT' in mode_calls
        assert 'OBJECT' in mode_calls


if __name__ == '__main__':
    unittest.main()
