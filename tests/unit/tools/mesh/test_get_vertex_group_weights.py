"""Tests for mesh vertex group weights introspection."""
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


class TestMeshGetVertexGroupWeights(unittest.TestCase):
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

        vg_spine = MagicMock()
        vg_spine.name = "Spine"
        vg_spine.index = 0
        vg_arm = MagicMock()
        vg_arm.name = "Arm"
        vg_arm.index = 1

        vertex_groups = MagicMock()
        vertex_groups.__iter__.return_value = iter([vg_spine, vg_arm])
        vertex_groups.__len__.return_value = 2
        vertex_groups.get.side_effect = lambda name: vg_spine if name == "Spine" else None
        obj.vertex_groups = vertex_groups

        v0 = MagicMock()
        v0.index = 0
        g0 = MagicMock()
        g0.group = 0
        g0.weight = 1.0
        v0.groups = [g0]

        v1 = MagicMock()
        v1.index = 1
        g1 = MagicMock()
        g1.group = 0
        g1.weight = 0.5
        g2 = MagicMock()
        g2.group = 1
        g2.weight = 0.2
        v1.groups = [g1, g2]

        obj.data = MagicMock()
        obj.data.vertices = [v0, v1]
        bpy.data.objects = {"Cube": obj}

        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        bm.verts = MagicMock()
        bm.verts.ensure_lookup_table = MagicMock()
        bv0 = MagicMock(index=0, select=True)
        bv1 = MagicMock(index=1, select=False)
        bm.verts.__iter__.return_value = iter([bv0, bv1])

        return obj

    def test_get_vertex_group_weights_group_selected_only(self):
        self._setup_object()

        result = self.handler.get_vertex_group_weights("Cube", group_name="Spine", selected_only=True)

        assert result["group_name"] == "Spine"
        assert result["selected_count"] == 1
        assert result["returned_count"] == 1
        assert result["weights"][0]["vert"] == 0
        assert result["weights"][0]["weight"] == 1.0

    def test_get_vertex_group_weights_all_groups(self):
        self._setup_object()

        result = self.handler.get_vertex_group_weights("Cube", group_name=None, selected_only=False)

        assert result["group_count"] == 2
        assert result["groups"][0]["name"] == "Spine"
        assert result["groups"][0]["weight_count"] == 2
        assert result["groups"][1]["name"] == "Arm"
        assert result["groups"][1]["weight_count"] == 1


if __name__ == '__main__':
    unittest.main()
