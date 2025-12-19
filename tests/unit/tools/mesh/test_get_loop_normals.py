"""Tests for mesh loop normals introspection."""
import unittest
from unittest.mock import MagicMock
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
if 'bmesh' not in sys.modules:
    sys.modules['bmesh'] = MagicMock()

import bpy
import bmesh

from blender_addon.application.handlers.mesh import MeshHandler


class TestMeshGetLoopNormals(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        bpy.context.view_layer = MagicMock()
        bpy.context.view_layer.objects.active = None
        bpy.data.objects = {}
        bpy.ops.object.mode_set = MagicMock()
        bmesh.from_edit_mesh = MagicMock()
        bmesh.update_edit_mesh = MagicMock()

    def test_get_loop_normals_selected_only(self):
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'

        mesh = MagicMock()
        mesh.use_auto_smooth = True
        mesh.has_custom_normals = True
        mesh.calc_normals_split = MagicMock()
        mesh.free_normals_split = MagicMock()

        loop0 = MagicMock()
        loop0.vertex_index = 0
        loop0.normal = MagicMock(x=0.0, y=0.0, z=1.0)
        loop1 = MagicMock()
        loop1.vertex_index = 1
        loop1.normal = MagicMock(x=0.0, y=1.0, z=0.0)
        loop2 = MagicMock()
        loop2.vertex_index = 2
        loop2.normal = MagicMock(x=1.0, y=0.0, z=0.0)
        loop3 = MagicMock()
        loop3.vertex_index = 3
        loop3.normal = MagicMock(x=1.0, y=1.0, z=1.0)
        mesh.loops = [loop0, loop1, loop2, loop3]

        poly0 = MagicMock(index=0, loop_start=0, loop_total=2)
        poly1 = MagicMock(index=1, loop_start=2, loop_total=2)
        mesh.polygons = [poly0, poly1]

        obj.data = mesh
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        bm.faces = MagicMock()
        bm.faces.ensure_lookup_table = MagicMock()

        face0 = MagicMock(index=0, select=False)
        face1 = MagicMock(index=1, select=True)
        bm.faces.__iter__.return_value = iter([face0, face1])

        result = self.handler.get_loop_normals("Cube", selected_only=True)

        assert result["loop_count"] == 4
        assert result["selected_count"] == 2
        assert result["returned_count"] == 2
        assert result["loops"][0]["loop_index"] == 2
        assert result["auto_smooth"] is True
        assert result["custom_normals"] is True


if __name__ == '__main__':
    unittest.main()
