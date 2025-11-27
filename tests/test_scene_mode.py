import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock blender modules before import
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
import bpy

# Import after mocking
from blender_addon.application.handlers.scene import SceneHandler

class TestSceneMode(unittest.TestCase):
    def setUp(self):
        self.handler = SceneHandler()
        # Reset mocks
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.location = (0.0, 0.0, 0.0)
        self.cube.rotation_euler = (0.0, 0.0, 0.0)
        self.cube.scale = (1.0, 1.0, 1.0)
        self.cube.dimensions = (2.0, 2.0, 2.0)
        self.cube.users_collection = []
        self.cube.material_slots = []
        self.cube.modifiers = []
        self.cube.keys = MagicMock(return_value=[])
        self.cube.get = MagicMock()
        self.cube.evaluated_get = MagicMock(return_value=self.cube)
        self.light = MagicMock()
        self.light.name = "Light"

        bpy.context.mode = 'OBJECT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.active_object = self.cube
        bpy.context.selected_objects = [self.cube, self.light]
        bpy.data.objects = {"Cube": self.cube}

    def test_set_mode_valid(self):
        # Execute
        result = self.handler.set_mode('EDIT')
        
        # Verify
        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')
        self.assertIn("Switched to EDIT mode", result)

    def test_set_mode_already_set(self):
        # Setup
        bpy.context.mode = 'EDIT'
        
        # Execute
        result = self.handler.set_mode('EDIT')
        
        # Verify
        bpy.ops.object.mode_set.assert_not_called()
        self.assertIn("Already in EDIT mode", result)

    def test_set_mode_no_active_object(self):
        # Setup
        bpy.context.active_object = None

        # Execute & Verify
        with self.assertRaises(ValueError):
            self.handler.set_mode('EDIT')

    def test_get_mode_returns_selection_summary(self):
        bpy.context.mode = 'EDIT_MESH'
        result = self.handler.get_mode()
        self.assertEqual(result["mode"], 'EDIT_MESH')
        self.assertEqual(result["active_object"], 'Cube')
        self.assertEqual(result["active_object_type"], 'MESH')
        self.assertEqual(result["selection_count"], 2)
        self.assertIn('Cube', result["selected_object_names"])
        self.assertIn('Light', result["selected_object_names"])

    def test_list_selection_object_mode(self):
        bpy.context.mode = 'OBJECT'
        summary = self.handler.list_selection()
        self.assertEqual(summary["mode"], 'OBJECT')
        self.assertEqual(summary["selection_count"], 2)
        self.assertIsNone(summary["edit_mode_vertex_count"])

    def test_inspect_object_basic(self):
        self.cube.type = 'LIGHT'
        report = self.handler.inspect_object("Cube")
        self.assertEqual(report["object_name"], "Cube")
        self.assertEqual(report["material_slots"], [])

    def test_inspect_object_missing(self):
        bpy.data.objects = {}
        with self.assertRaises(ValueError):
            self.handler.inspect_object("Missing")

if __name__ == '__main__':
    unittest.main()
