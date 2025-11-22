import unittest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock bpy before importing addon code
sys.modules["bpy"] = MagicMock()
import bpy

# Configure Mock context
bpy.context.scene.objects = []
bpy.data.objects = {}

# Import handler
from blender_addon.api import scene

class TestSceneTools(unittest.TestCase):
    def setUp(self):
        # Reset mock data
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.location = (0, 0, 0)
        
        bpy.context.scene.objects = [self.cube]
        
        # Mock bpy.data.objects as a dict-like object
        bpy.data.objects = MagicMock()
        bpy.data.objects.__getitem__.side_effect = lambda k: self.cube if k == "Cube" else KeyError(k)
        bpy.data.objects.__contains__.side_effect = lambda k: k == "Cube"
        bpy.data.objects.remove = MagicMock()

    def test_list_objects(self):
        result = scene.list_objects()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Cube")

    def test_delete_object(self):
        scene.delete_object("Cube")
        bpy.data.objects.remove.assert_called_with(self.cube, do_unlink=True)

    def test_delete_nonexistent_object(self):
        with self.assertRaises(ValueError):
            scene.delete_object("Ghost")

if __name__ == "__main__":
    unittest.main()