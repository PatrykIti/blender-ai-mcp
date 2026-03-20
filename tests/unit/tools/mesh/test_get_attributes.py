"""Tests for mesh attributes introspection."""
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


class TestMeshGetAttributes(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        bpy.context.view_layer = MagicMock()
        bpy.context.view_layer.objects.active = None
        bpy.data.objects = {}
        bpy.ops.object.mode_set = MagicMock()
        bmesh.from_edit_mesh = MagicMock()

    def _setup_object(self):
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'OBJECT'

        data0 = MagicMock()
        data0.color = [0.1, 0.2, 0.3, 1.0]
        data1 = MagicMock()
        data1.color = [0.4, 0.5, 0.6, 1.0]

        attr_color = MagicMock()
        attr_color.name = "Col"
        attr_color.data_type = "FLOAT_COLOR"
        attr_color.domain = "POINT"
        attr_color.data = [data0, data1]

        attributes = MagicMock()
        attributes.__iter__.return_value = iter([attr_color])
        attributes.get.side_effect = lambda name: attr_color if name == "Col" else None

        mesh = MagicMock()
        mesh.attributes = attributes
        obj.data = mesh
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        bm.verts = MagicMock()
        bm.edges = MagicMock()
        bm.faces = MagicMock()
        bm.verts.ensure_lookup_table = MagicMock()
        bm.edges.ensure_lookup_table = MagicMock()
        bm.faces.ensure_lookup_table = MagicMock()
        bv0 = MagicMock(index=0, select=True)
        bv1 = MagicMock(index=1, select=False)
        bm.verts.__iter__.return_value = iter([bv0, bv1])
        bm.edges.__iter__.return_value = iter([])
        bm.faces.__iter__.return_value = iter([])

        return obj

    def test_get_attributes_list(self):
        self._setup_object()

        result = self.handler.get_attributes("Cube")

        assert result["attribute_count"] == 1
        assert result["attributes"][0]["name"] == "Col"
        assert result["attributes"][0]["domain"] == "POINT"

    def test_get_attributes_data_selected_only(self):
        self._setup_object()

        result = self.handler.get_attributes("Cube", attribute_name="Col", selected_only=True)

        assert result["attribute"]["name"] == "Col"
        assert result["selected_count"] == 1
        assert result["returned_count"] == 1
        assert result["values"][0]["index"] == 0
        assert result["values"][0]["value"] == [0.1, 0.2, 0.3, 1.0]


if __name__ == '__main__':
    unittest.main()
