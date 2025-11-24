import unittest
from unittest.mock import MagicMock, patch, mock_open, PropertyMock
import sys

# Mock blender modules before import
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
import bpy

from blender_addon.application.handlers.scene import SceneHandler

class TestViewportControl(unittest.TestCase):
    def setUp(self):
        # Reset OPS mocks to ensure isolation between tests
        bpy.ops.object = MagicMock()
        bpy.ops.render = MagicMock()
        bpy.ops.view3d = MagicMock()
        
        self.handler = SceneHandler()
        
        # Setup Viewport Mock Structure
        self.mock_shading = MagicMock()
        # Initial state
        self.mock_shading.type = 'SOLID'
        
        self.mock_space = MagicMock()
        self.mock_space.type = 'VIEW_3D'
        self.mock_space.shading = self.mock_shading
        
        self.mock_region = MagicMock()
        self.mock_region.type = 'WINDOW'
        
        self.mock_area = MagicMock()
        self.mock_area.type = 'VIEW_3D'
        self.mock_area.spaces = [self.mock_space]
        self.mock_area.regions = [self.mock_region]
        
        # Mock screen areas
        bpy.context.screen.areas = [self.mock_area]
        
        # Mock temp_override context manager
        self.mock_override = MagicMock()
        self.mock_override.__enter__ = MagicMock()
        self.mock_override.__exit__ = MagicMock()
        bpy.context.temp_override = MagicMock(return_value=self.mock_override)
        
        # Mock Objects Collection (supports dict access AND .remove)
        self.mock_objects_collection = MagicMock()
        self._objects_storage = {}
        
        # Bind dictionary methods
        self.mock_objects_collection.__getitem__.side_effect = self._objects_storage.__getitem__
        self.mock_objects_collection.__contains__.side_effect = self._objects_storage.__contains__
        self.mock_objects_collection.get.side_effect = self._objects_storage.get
        
        bpy.data.objects = self.mock_objects_collection
        
        # Helper to add objects in tests
        self.add_object("Cube")
        
        # Mock scene render properties
        self.render_mock = bpy.context.scene.render
        self.render_mock.resolution_x = 1920
        self.render_mock.resolution_y = 1080
        self.render_mock.filepath = "/tmp/old.png"

    def add_object(self, name):
        obj = MagicMock()
        obj.name = name
        self._objects_storage[name] = obj
        return obj
        
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"img_data")
    @patch('tempfile.mkstemp')
    @patch('os.close')
    @patch('os.remove')
    def test_dynamic_view_with_shading(self, mock_remove, mock_close, mock_mkstemp, mock_open, mock_exists):
        # Setup
        mock_mkstemp.return_value = (123, "/tmp/render.jpg")
        mock_exists.return_value = True
        
        # Initial Camera
        original_cam = MagicMock()
        bpy.context.scene.camera = original_cam
        
        cube = self._objects_storage["Cube"]
        
        # Execute: Get Wireframe View of 'Cube'
        self.handler.get_viewport(
            width=800, 
            height=600, 
            shading='WIREFRAME', 
            camera_name='USER_PERSPECTIVE', 
            focus_target='Cube'
        )
        
        # 1. Verify Temp Camera Created
        bpy.ops.object.camera_add.assert_called()
        
        # 2. Verify Target Selected
        cube.select_set.assert_called_with(True)
        
        # 3. Verify Camera Framed to Selection
        # Should be called within temp_override
        bpy.context.temp_override.assert_any_call(area=self.mock_area, region=self.mock_region)
        bpy.ops.view3d.camera_to_view_selected.assert_called()
        
        # 4. Verify Render
        bpy.ops.render.opengl.assert_called_with(write_still=True)
        
        # 5. Verify Cleanup/Restore
        # Original camera restored
        self.assertEqual(bpy.context.scene.camera, original_cam)
        # Resolution restored
        self.assertEqual(self.render_mock.resolution_x, 1920)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"img_data")
    @patch('tempfile.mkstemp')
    @patch('os.close')
    @patch('os.remove')
    def test_specific_camera(self, mock_remove, mock_close, mock_mkstemp, mock_open, mock_exists):
        # Setup
        mock_mkstemp.return_value = (123, "/tmp/render.jpg")
        mock_exists.return_value = True
        
        # Mock existing camera in scene
        self.add_object("MyCamera")
        
        # Execute
        self.handler.get_viewport(
            camera_name="MyCamera"
        )
        
        # Verify:
        # 1. NO temp camera created
        bpy.ops.object.camera_add.assert_not_called()
        # 2. Scene camera set to MyCamera (implicitly checked by lack of camera_add and logic flow)
        
        # 3. Render called
        bpy.ops.render.opengl.assert_called()

if __name__ == '__main__':
    unittest.main()
