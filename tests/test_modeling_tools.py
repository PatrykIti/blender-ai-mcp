import unittest
from unittest.mock import MagicMock
import sys
import importlib

# Ensure bpy is mocked globally BEFORE any import
if "bpy" not in sys.modules:
    sys.modules["bpy"] = MagicMock()
import bpy

# Import module under test
import blender_addon.application.handlers.modeling

class MockObjects(dict):
    """Helper to mock bpy.data.objects which acts as a dict but has methods like remove."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove = MagicMock()

class TestModelingTools(unittest.TestCase):
    def setUp(self):
        # 1. Reset bpy mocks completely
        # It is crucial to reset the MagicMock attributes to clear previous calls
        bpy.ops = MagicMock()
        bpy.context = MagicMock()
        bpy.data = MagicMock()
        
        # 2. Setup Operators
        # Create explicit mock for primitive_cube_add
        bpy.ops.mesh.primitive_cube_add = MagicMock()
        
        # 3. Setup Active Object
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.location = (0,0,0)
        self.cube.scale = (1,1,1)
        self.cube.modifiers = MagicMock()
        
        bpy.context.active_object = self.cube
        
        # 4. Setup bpy.data.objects using MockObjects (dict)
        self.objects_mock = MockObjects()
        self.objects_mock["Cube"] = self.cube
        bpy.data.objects = self.objects_mock

        # 5. Reload module to ensure it picks up the Reset bpy
        importlib.reload(blender_addon.application.handlers.modeling)
        from blender_addon.application.handlers.modeling import ModelingHandler
        
        self.handler = ModelingHandler()

    def test_create_cube(self):
        # When
        result = self.handler.create_primitive("Cube", size=3.0, location=(1,2,3))
        
        # Then
        bpy.ops.mesh.primitive_cube_add.assert_called_with(size=3.0, location=(1,2,3), rotation=(0,0,0))
        self.assertEqual(result["name"], "Cube")

    def test_transform_object(self):
        # When
        self.handler.transform_object("Cube", location=(10,10,10))
        
        # Then
        self.assertEqual(self.cube.location, (10,10,10))

    def test_add_modifier(self):
        # Setup
        mod_mock = MagicMock()
        mod_mock.name = "Subdiv"
        self.cube.modifiers.new.return_value = mod_mock
        
        # When
        result = self.handler.add_modifier("Cube", "SUBSURF", {"levels": 2})
        
        # Then
        self.cube.modifiers.new.assert_called_with(name="SUBSURF", type="SUBSURF")
        self.assertEqual(mod_mock.levels, 2)
        self.assertEqual(result["modifier"], "Subdiv")

if __name__ == "__main__":
    unittest.main()
