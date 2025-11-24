import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys

# Mock blender modules before import
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
import bpy

# Import after mocking
from blender_addon.application.handlers.scene import SceneHandler

class TestSceneHandlerExtended(unittest.TestCase):
    def setUp(self):
        self.handler = SceneHandler()
        # Reset mocks
        bpy.data.objects = {}
        bpy.context.scene.objects = []
        bpy.ops.object = MagicMock()
        bpy.ops.render = MagicMock()
        bpy.ops.transform = MagicMock()
        bpy.ops.view3d = MagicMock()
        bpy.context.view_layer.objects.active = None

    def test_duplicate_object(self):
        # Setup
        original_obj = MagicMock()
        original_obj.name = "Cube"
        original_obj.location = (0, 0, 0)
        bpy.data.objects = {"Cube": original_obj}
        
        # Mock active object change after duplicate
        new_obj = MagicMock()
        new_obj.name = "Cube.001"
        new_obj.location = (2, 0, 0) # After translation
        
        # When duplicate is called, update active object
        def duplicate_side_effect():
            bpy.context.view_layer.objects.active = new_obj
            
        bpy.ops.object.duplicate.side_effect = duplicate_side_effect

        # Execute
        result = self.handler.duplicate_object("Cube", translation=[2.0, 0.0, 0.0])

        # Verify
        bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        original_obj.select_set.assert_called_with(True)
        bpy.ops.object.duplicate.assert_called()
        bpy.ops.transform.translate.assert_called_with(value=[2.0, 0.0, 0.0])
        
        self.assertEqual(result['original'], "Cube")
        self.assertEqual(result['new_object'], "Cube.001")

    def test_set_active_object(self):
        # Setup
        obj = MagicMock()
        obj.name = "Cube"
        bpy.data.objects = {"Cube": obj}

        # Execute
        result = self.handler.set_active_object("Cube")

        # Verify
        bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        obj.select_set.assert_called_with(True)
        self.assertEqual(bpy.context.view_layer.objects.active, obj)
        self.assertEqual(result['active'], "Cube")

if __name__ == '__main__':
    unittest.main()
