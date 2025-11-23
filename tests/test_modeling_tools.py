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
        bpy.ops.object.convert = MagicMock()
        bpy.ops.object.join = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.separate = MagicMock()
        bpy.ops.object.origin_set = MagicMock()
        
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

    def test_convert_to_mesh(self):
        # Setup a non-mesh object (e.g., Curve)
        curve_obj = MagicMock()
        curve_obj.name = "BezierCurve"
        curve_obj.type = 'CURVE'
        
        self.objects_mock["BezierCurve"] = curve_obj # Add to bpy.data.objects
        bpy.context.active_object = curve_obj # Set as active before conversion
        
        bpy.ops.object.convert = MagicMock() # Mock the convert operator
        
        # When
        result = self.handler.convert_to_mesh("BezierCurve")
        
        # Then
        bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        curve_obj.select_set.assert_called_with(True)
        bpy.ops.object.convert.assert_called_with(target='MESH')
        self.assertEqual(result['name'], "BezierCurve")
        self.assertEqual(result['type'], "MESH")
        self.assertEqual(result['status'], "converted")

    def test_convert_to_mesh_already_mesh(self):
        # Setup a mesh object
        mesh_obj = MagicMock()
        mesh_obj.name = "Cube"
        mesh_obj.type = 'MESH'
        
        self.objects_mock["Cube"] = mesh_obj
        
        # When
        result = self.handler.convert_to_mesh("Cube")
        
        # Then
        bpy.ops.object.convert.assert_not_called()
        self.assertEqual(result['name'], "Cube")
        self.assertEqual(result['type'], "MESH")
        self.assertEqual(result['status'], "already_mesh")

    def test_convert_to_mesh_object_not_found(self):
        with self.assertRaisesRegex(ValueError, "Object 'NonExistent' not found"):
            self.handler.convert_to_mesh("NonExistent")

    def test_join_objects(self):
        # Setup two more objects
        obj1 = MagicMock()
        obj1.name = "Sphere"
        obj1.select_set = MagicMock()
        
        obj2 = MagicMock()
        obj2.name = "Cylinder"
        obj2.select_set = MagicMock()

        # Add them to our mock data
        self.objects_mock["Sphere"] = obj1
        self.objects_mock["Cylinder"] = obj2
        
        # Mock the active object after join. Blender operator replaces active object
        joined_obj = MagicMock()
        joined_obj.name = "Sphere"
        bpy.context.active_object = joined_obj # This mock will be the result of join
        
        bpy.ops.object.join = MagicMock() # Mock the join operator
        
        # When
        result = self.handler.join_objects(["Cube", "Sphere", "Cylinder"])
        
        # Then
        bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        self.cube.select_set.assert_called_with(True)
        obj1.select_set.assert_called_with(True)
        obj2.select_set.assert_called_with(True)
        bpy.ops.object.join.assert_called_once()
        self.assertEqual(result['name'], "Sphere")
        self.assertEqual(result['joined_count'], 3)

    def test_join_objects_no_objects(self):
        with self.assertRaisesRegex(ValueError, "No objects provided for joining."):
            self.handler.join_objects([])

    def test_join_objects_non_existent(self):
        # Setup one existing, one non-existent
        self.objects_mock["Sphere"] = MagicMock()
        
        with self.assertRaisesRegex(ValueError, "Object 'NonExistent' not found"):
            self.handler.join_objects(["Cube", "NonExistent"])

    def test_separate_object_loose(self):
        # Setup
        obj_to_separate = MagicMock()
        obj_to_separate.name = "ComplexMesh"
        obj_to_separate.type = 'MESH'
        obj_to_separate.select_set = MagicMock()

        self.objects_mock["ComplexMesh"] = obj_to_separate
        
        # Mock initial scene objects and new objects after separation
        bpy.context.scene.objects = [obj_to_separate] # Initial
        
        new_part1 = MagicMock()
        new_part1.name = "ComplexMesh.001"
        new_part2 = MagicMock()
        new_part2.name = "ComplexMesh.002"

        def separate_side_effect(**kwargs):
            # Simulate new objects appearing in scene after separation
            bpy.context.scene.objects.extend([new_part1, new_part2])
            
        bpy.ops.mesh.separate.side_effect = separate_side_effect
        
        # When
        result = self.handler.separate_object("ComplexMesh", "LOOSE")

        # Then
        bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        obj_to_separate.select_set.assert_called_with(True)
        bpy.ops.object.mode_set.assert_any_call(mode='EDIT')
        bpy.ops.mesh.separate.assert_called_with(type='LOOSE')
        bpy.ops.object.mode_set.assert_any_call(mode='OBJECT')
        self.assertIn("ComplexMesh.001", result["separated_objects"])
        self.assertIn("ComplexMesh.002", result["separated_objects"])
        self.assertEqual(result["original_object"], "ComplexMesh")

    def test_separate_object_non_mesh(self):
        # Setup a non-mesh object
        curve_obj = MagicMock()
        curve_obj.name = "BezierCurve"
        curve_obj.type = 'CURVE'
        self.objects_mock["BezierCurve"] = curve_obj

        with self.assertRaisesRegex(ValueError, "Object 'BezierCurve' is not a mesh"):
            self.handler.separate_object("BezierCurve", "LOOSE")

    def test_separate_object_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "Invalid separation type: 'INVALID'. Must be one of \\['LOOSE\', 'SELECTED\', 'MATERIAL'\\]"):
            self.handler.separate_object("Cube", "INVALID")

    def test_separate_object_not_found(self):
        with self.assertRaisesRegex(ValueError, "Object 'NonExistent' not found"):
            self.handler.separate_object("NonExistent", "LOOSE")

    def test_set_origin(self):
        # Setup
        obj = MagicMock()
        obj.name = "TestObject"
        obj.select_set = MagicMock()
        self.objects_mock["TestObject"] = obj
        
        bpy.ops.object.origin_set = MagicMock()

        # When
        result = self.handler.set_origin("TestObject", "ORIGIN_GEOMETRY_TO_CURSOR")
        
        # Then
        bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        obj.select_set.assert_called_with(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.origin_set.assert_called_with(type='ORIGIN_GEOMETRY_TO_CURSOR')
        self.assertEqual(result['object'], "TestObject")
        self.assertEqual(result['origin_type'], "ORIGIN_GEOMETRY_TO_CURSOR")
        self.assertEqual(result['status'], "success")

    def test_set_origin_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "Invalid origin type: 'INVALID_TYPE'. Must be one of"):
            self.handler.set_origin("Cube", "INVALID_TYPE")

    def test_set_origin_object_not_found(self):
        with self.assertRaisesRegex(ValueError, "Object 'NonExistent' not found"):
            self.handler.set_origin("NonExistent", "ORIGIN_GEOMETRY_TO_CURSOR")

if __name__ == "__main__":
    unittest.main()
