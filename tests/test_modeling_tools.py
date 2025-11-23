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
        result = self.handler.add_modifier("Cube", "subsurf", {"levels": 2}) # Lowercase input
        
        # Then
        # Expect Uppercase "SUBSURF" passed to new()
        self.cube.modifiers.new.assert_called_with(name="subsurf", type="SUBSURF")
        self.assertEqual(mod_mock.levels, 2)
        self.assertEqual(result["modifier"], "Subdiv")

    def test_apply_modifier(self):
        # Setup: Ensure the object has a modifier mock
        mod_name = "MirrorMod"
        mock_modifier = MagicMock()
        mock_modifier.name = mod_name
        
        # Update contains logic to support both direct check and iteration
        def contains_side_effect(key):
            return key == mod_name
        
        self.cube.modifiers.__contains__.side_effect = contains_side_effect
        self.cube.modifiers.__getitem__.side_effect = lambda k: mock_modifier if k == mod_name else KeyError(k)
        
        # Mock iteration for case-insensitive search fallback
        self.cube.modifiers.__iter__.return_value = [mock_modifier]
        
        bpy.ops.object.modifier_apply = MagicMock()
        
        # When
        result = self.handler.apply_modifier("Cube", mod_name)
        
        # Then
        bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        self.cube.select_set.assert_called_with(True)
        bpy.ops.object.modifier_apply.assert_called_with(modifier=mod_name)
        self.assertEqual(result['applied_modifier'], mod_name)
        self.assertEqual(result['object'], "Cube")

    def test_apply_modifier_case_insensitive(self):
        # Setup: Modifier is named "BEVEL", request is for "bevel"
        real_mod_name = "BEVEL"
        request_mod_name = "bevel"
        
        mock_modifier = MagicMock()
        mock_modifier.name = real_mod_name
        
        # Contains returns False for "bevel" to trigger fallback logic
        self.cube.modifiers.__contains__.side_effect = lambda k: k == real_mod_name
        
        # Iterator returns the modifier with Uppercase name
        self.cube.modifiers.__iter__.return_value = [mock_modifier]
        
        bpy.ops.object.modifier_apply = MagicMock()
        
        # When
        result = self.handler.apply_modifier("Cube", request_mod_name)
        
        # Then
        # Should find "BEVEL" and use it
        bpy.ops.object.modifier_apply.assert_called_with(modifier=real_mod_name)
        self.assertEqual(result['applied_modifier'], real_mod_name)

    def test_apply_modifier_object_not_found(self):
        with self.assertRaisesRegex(ValueError, "Object 'NonExistent' not found"):
            self.handler.apply_modifier("NonExistent", "SomeMod")

    def test_apply_modifier_not_found_on_object(self):
        # Setup: Object exists, but no such modifier
        mod_name = "NonExistentMod"
        
        # We need to mock modifiers collection for the 'Cube'
        modifiers_mock = MagicMock()
        modifiers_mock.__contains__.side_effect = lambda k: False # Not found directly
        modifiers_mock.__iter__.return_value = [] # Empty iteration (fallback fails)
        self.cube.modifiers = modifiers_mock

        with self.assertRaisesRegex(ValueError, f"Modifier \'{mod_name}\' not found on object 'Cube'"):
            self.handler.apply_modifier("Cube", mod_name)

if __name__ == "__main__":
    unittest.main()
