import unittest
from unittest.mock import MagicMock
import sys
import importlib

# Mock bpy BEFORE importing the module under test
if "bpy" not in sys.modules:
    sys.modules["bpy"] = MagicMock()
import bpy

# Import module
import blender_addon.application.handlers.modeling

class TestModelingTools(unittest.TestCase):
    def setUp(self):
        # Reload module to ensure clean state
        importlib.reload(blender_addon.application.handlers.modeling)
        from blender_addon.application.handlers.modeling import ModelingHandler
        
        self.handler = ModelingHandler()
        
        # Reset mocks
        bpy.ops.mesh.primitive_cube_add = MagicMock()
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.name = "Cube"
        
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.location = (0,0,0)
        self.cube.scale = (1,1,1)
        self.cube.modifiers = MagicMock()
        
        # Correct way to mock bpy.data.objects dict access
        bpy.data.objects = MagicMock()
        bpy.data.objects.__getitem__.side_effect = lambda k: self.cube if k == "Cube" else KeyError(k)
        bpy.data.objects.__contains__.side_effect = lambda k: k == "Cube"

    def test_create_cube(self):
        result = self.handler.create_primitive("Cube", size=3.0, location=(1,2,3))
        bpy.ops.mesh.primitive_cube_add.assert_called_with(size=3.0, location=(1,2,3), rotation=(0,0,0))
        self.assertEqual(result["name"], "Cube")

    def test_transform_object(self):
        self.handler.transform_object("Cube", location=(10,10,10))
        self.assertEqual(self.cube.location, (10,10,10))

    def test_add_modifier(self):
        mod_mock = MagicMock()
        mod_mock.name = "Subdiv"
        self.cube.modifiers.new.return_value = mod_mock
        
        result = self.handler.add_modifier("Cube", "SUBSURF", {"levels": 2})
        
        self.cube.modifiers.new.assert_called_with(name="SUBSURF", type="SUBSURF")
        self.assertEqual(mod_mock.levels, 2) # Check if property was set
        self.assertEqual(result["modifier"], "Subdiv")

if __name__ == "__main__":
    unittest.main()
