"""Tests for mesh shape key introspection."""
import unittest
from unittest.mock import MagicMock
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
if 'bmesh' not in sys.modules:
    sys.modules['bmesh'] = MagicMock()

import bpy

from blender_addon.application.handlers.mesh import MeshHandler


class Vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class TestMeshGetShapeKeys(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()

        bpy.context.view_layer = MagicMock()
        bpy.context.view_layer.objects.active = None
        bpy.data.objects = {}
        bpy.ops.object.mode_set = MagicMock()

    def test_get_shape_keys_with_deltas(self):
        obj = MagicMock()
        obj.type = 'MESH'
        obj.mode = 'EDIT'

        basis_point0 = MagicMock()
        basis_point0.co = Vec(0.0, 0.0, 0.0)
        basis_point1 = MagicMock()
        basis_point1.co = Vec(1.0, 1.0, 1.0)

        smile_point0 = MagicMock()
        smile_point0.co = Vec(0.1, 0.0, 0.0)
        smile_point1 = MagicMock()
        smile_point1.co = Vec(1.0, 1.0, 1.0)

        basis = MagicMock()
        basis.name = "Basis"
        basis.value = 0.0
        basis.data = [basis_point0, basis_point1]

        smile = MagicMock()
        smile.name = "Smile"
        smile.value = 0.2
        smile.data = [smile_point0, smile_point1]

        shape_keys = MagicMock()
        shape_keys.key_blocks = [basis, smile]

        obj.data = MagicMock()
        obj.data.shape_keys = shape_keys
        bpy.data.objects = {"Cube": obj}

        result = self.handler.get_shape_keys("Cube", include_deltas=True)

        assert result["shape_key_count"] == 2
        assert result["shape_keys"][0]["name"] == "Basis"
        assert result["shape_keys"][0]["deltas"] == []
        assert result["shape_keys"][1]["name"] == "Smile"
        assert result["shape_keys"][1]["deltas"] == [{"vert": 0, "delta": [0.1, 0.0, 0.0]}]


if __name__ == '__main__':
    unittest.main()
