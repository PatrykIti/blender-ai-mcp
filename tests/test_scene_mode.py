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
        bpy.context.mode = 'OBJECT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.active_object = MagicMock()

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

if __name__ == '__main__':
    unittest.main()
