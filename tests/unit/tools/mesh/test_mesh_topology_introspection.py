"""Tests for mesh topology introspection tools (edges, faces, UVs)."""
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


class MeshHandlerTestBase(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        bpy.context.view_layer = MagicMock()
        bpy.context.view_layer.objects.active = None
        bpy.data.objects = {}
        bpy.ops.object.mode_set = MagicMock()
        bmesh.from_edit_mesh = MagicMock()


class TestMeshGetEdgeData(MeshHandlerTestBase):
    def test_get_edge_data_selected_only(self):
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'
        obj.data = MagicMock()
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        bm.verts = MagicMock()
        bm.verts.ensure_lookup_table = MagicMock()
        bm.edges = MagicMock()
        bm.edges.ensure_lookup_table = MagicMock()

        v0 = MagicMock()
        v0.index = 0
        v1 = MagicMock()
        v1.index = 1
        v2 = MagicMock()
        v2.index = 2

        edge0 = MagicMock()
        edge0.index = 0
        edge0.verts = [v0, v1]
        edge0.is_boundary = False
        edge0.is_manifold = True
        edge0.seam = False
        edge0.smooth = True
        edge0.crease = 0.25
        edge0.bevel_weight = 1.0
        edge0.select = True

        edge1 = MagicMock()
        edge1.index = 1
        edge1.verts = [v1, v2]
        edge1.is_boundary = True
        edge1.is_manifold = False
        edge1.seam = True
        edge1.smooth = False
        edge1.crease = 0.0
        edge1.bevel_weight = 0.0
        edge1.select = False

        edges = [edge0, edge1]
        bm.edges.__iter__.return_value = iter(edges)
        bm.edges.__len__.return_value = len(edges)

        result = self.handler.get_edge_data("Cube", selected_only=True)

        assert result["edge_count"] == 2
        assert result["selected_count"] == 1
        assert result["returned_count"] == 1
        assert result["edges"][0]["index"] == 0
        assert result["edges"][0]["is_sharp"] == False


class TestMeshGetFaceData(MeshHandlerTestBase):
    def test_get_face_data_all_faces(self):
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'
        obj.data = MagicMock()
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        bm.verts = MagicMock()
        bm.verts.ensure_lookup_table = MagicMock()
        bm.faces = MagicMock()
        bm.faces.ensure_lookup_table = MagicMock()

        v0 = MagicMock()
        v0.index = 0
        v1 = MagicMock()
        v1.index = 1
        v2 = MagicMock()
        v2.index = 2

        normal = MagicMock()
        normal.x = 0.0
        normal.y = 0.0
        normal.z = 1.0

        center = MagicMock()
        center.x = 0.1
        center.y = 0.2
        center.z = 0.3

        face = MagicMock()
        face.index = 0
        face.verts = [v0, v1, v2]
        face.normal = normal
        face.calc_center_median.return_value = center
        face.calc_area.return_value = 0.5
        face.material_index = 1
        face.select = True

        bm.faces.__iter__.return_value = iter([face])
        bm.faces.__len__.return_value = 1

        result = self.handler.get_face_data("Cube", selected_only=False)

        assert result["face_count"] == 1
        assert result["selected_count"] == 1
        assert result["returned_count"] == 1
        assert result["faces"][0]["material_index"] == 1
        assert result["faces"][0]["normal"] == [0.0, 0.0, 1.0]


class TestMeshGetUVData(MeshHandlerTestBase):
    def test_get_uv_data_active_layer(self):
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'
        obj.data = MagicMock()
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm

        bm.faces = MagicMock()
        bm.faces.ensure_lookup_table = MagicMock()

        uv_layer = MagicMock()
        uv_layer.name = "UVMap"

        uv_layers = MagicMock()
        uv_layers.get.return_value = uv_layer
        uv_layers.active = uv_layer

        bm.loops = MagicMock()
        bm.loops.layers = MagicMock()
        bm.loops.layers.uv = uv_layers

        loop0 = MagicMock()
        loop0.vert = MagicMock(index=0)
        uv0 = MagicMock()
        uv0.x = 0.0
        uv0.y = 0.1
        loop0.__getitem__.return_value = MagicMock(uv=uv0)

        loop1 = MagicMock()
        loop1.vert = MagicMock(index=1)
        uv1 = MagicMock()
        uv1.x = 0.5
        uv1.y = 0.1
        loop1.__getitem__.return_value = MagicMock(uv=uv1)

        loop2 = MagicMock()
        loop2.vert = MagicMock(index=2)
        uv2 = MagicMock()
        uv2.x = 0.5
        uv2.y = 0.6
        loop2.__getitem__.return_value = MagicMock(uv=uv2)

        face = MagicMock()
        face.index = 0
        face.select = True
        face.loops = [loop0, loop1, loop2]

        bm.faces.__iter__.return_value = iter([face])
        bm.faces.__len__.return_value = 1

        result = self.handler.get_uv_data("Cube")

        assert result["uv_layer"] == "UVMap"
        assert result["face_count"] == 1
        assert result["selected_count"] == 1
        assert result["faces"][0]["uvs"] == [[0.0, 0.1], [0.5, 0.1], [0.5, 0.6]]


if __name__ == '__main__':
    unittest.main()
