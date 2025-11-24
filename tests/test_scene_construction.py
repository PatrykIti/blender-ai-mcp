import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
import bpy

from blender_addon.application.handlers.scene import SceneHandler

class TestSceneConstruction(unittest.TestCase):
    def setUp(self):
        self.handler = SceneHandler()
        # Reset mocks
        bpy.data.lights.new = MagicMock()
        bpy.data.cameras.new = MagicMock()
        bpy.data.objects.new = MagicMock()
        bpy.context.collection.objects.link = MagicMock()
        
    def test_create_light(self):
        # Setup
        light_data = MagicMock()
        bpy.data.lights.new.return_value = light_data
        
        light_obj = MagicMock()
        light_obj.name = "MyLight"
        bpy.data.objects.new.return_value = light_obj
        
        # Execute
        result = self.handler.create_light(
            type='SPOT', 
            energy=500.0, 
            color=[1.0, 0.0, 0.0], 
            location=[1, 2, 3], 
            name="MyLight"
        )
        
        # Verify
        bpy.data.lights.new.assert_called_with(name="MyLight", type='SPOT')
        self.assertEqual(light_data.energy, 500.0)
        self.assertEqual(light_data.color, [1.0, 0.0, 0.0])
        
        bpy.data.objects.new.assert_called_with(name="MyLight", object_data=light_data)
        self.assertEqual(light_obj.location, [1, 2, 3])
        
        bpy.context.collection.objects.link.assert_called_with(light_obj)
        self.assertEqual(result, "MyLight")

    def test_create_camera(self):
        # Setup
        cam_data = MagicMock()
        bpy.data.cameras.new.return_value = cam_data
        
        cam_obj = MagicMock()
        cam_obj.name = "ShotCam"
        bpy.data.objects.new.return_value = cam_obj
        
        # Execute
        result = self.handler.create_camera(
            location=[0, -5, 1],
            rotation=[1.5, 0, 0],
            lens=85.0,
            clip_start=0.5,
            clip_end=200.0,
            name="ShotCam"
        )
        
        # Verify
        bpy.data.cameras.new.assert_called_with(name="ShotCam")
        self.assertEqual(cam_data.lens, 85.0)
        self.assertEqual(cam_data.clip_start, 0.5)
        self.assertEqual(cam_data.clip_end, 200.0)
        
        bpy.data.objects.new.assert_called_with(name="ShotCam", object_data=cam_data)
        self.assertEqual(cam_obj.location, [0, -5, 1])
        self.assertEqual(cam_obj.rotation_euler, [1.5, 0, 0])
        
        bpy.context.collection.objects.link.assert_called_with(cam_obj)
        self.assertEqual(result, "ShotCam")

    def test_create_empty(self):
        # Setup
        empty_obj = MagicMock()
        empty_obj.name = "Controller"
        bpy.data.objects.new.return_value = empty_obj
        
        # Execute
        result = self.handler.create_empty(
            type='CUBE',
            size=0.5,
            location=[1, 1, 1],
            name="Controller"
        )
        
        # Verify
        bpy.data.objects.new.assert_called_with("Controller", None)
        self.assertEqual(empty_obj.empty_display_type, 'CUBE')
        self.assertEqual(empty_obj.empty_display_size, 0.5)
        self.assertEqual(empty_obj.location, [1, 1, 1])
        
        bpy.context.collection.objects.link.assert_called_with(empty_obj)
        self.assertEqual(result, "Controller")

if __name__ == '__main__':
    unittest.main()
