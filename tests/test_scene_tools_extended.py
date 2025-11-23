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

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake_image_data")
    @patch('tempfile.mkstemp')
    @patch('os.close')
    @patch('os.remove')
    def test_get_viewport(self, mock_remove, mock_close, mock_mkstemp, mock_file_open, mock_exists):
        # Setup
        mock_mkstemp.return_value = (123, "/tmp/render.jpg")
        mock_exists.return_value = True
        
        # Mock camera scenario (no camera exists)
        bpy.context.scene.camera = None
        
        # Fix: Mock bpy.data.objects as a mock object, not a dict, because .remove() is called on it
        bpy.data.objects = MagicMock()

        # Setup PropertyMocks for resolution
        # We need to attach PropertyMock to the class/type of the object if possible, 
        # but here 'render' is a MagicMock instance. We can configure properties on the instance.
        render_mock = bpy.context.scene.render
        p_mock_x = unittest.mock.PropertyMock(return_value=1920)
        p_mock_y = unittest.mock.PropertyMock(return_value=1080)
        type(render_mock).resolution_x = p_mock_x
        type(render_mock).resolution_y = p_mock_y
        
        # Execute
        b64_result = self.handler.get_viewport(800, 600)
        
        # Verify
        # 1. Check if resolution was assigned properly using PropertyMock calls
        # We verify that the setters were called with 800 and 600
        # Note: PropertyMock records calls to the setter.
        
        # Check calls to resolution_x
        # Expectation: 
        # 1. Read original (getter)
        # 2. Set new (setter=800)
        # 3. Set original back (setter=original) - logic in handler restores it
        
        # Verify resolution_x assignment to 800
        p_mock_x.assert_any_call(800)
        
        # Verify resolution_y assignment to 600
        p_mock_y.assert_any_call(600)
        
        # 2. Camera created
        bpy.ops.object.camera_add.assert_called()
        
        # 3. Render called
        bpy.ops.render.opengl.assert_called_with(write_still=True)
        
        # 4. File read
        mock_file_open.assert_called_with("/tmp/render.jpg", "rb")
        
        # 5. Cleanup
        mock_remove.assert_called_with("/tmp/render.jpg")
        
        # 6. Result is base64
        import base64
        expected = base64.b64encode(b"fake_image_data").decode('utf-8')
        self.assertEqual(b64_result, expected)

if __name__ == '__main__':
    unittest.main()
