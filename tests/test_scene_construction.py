import sys
import pytest
from unittest.mock import MagicMock

# conftest.py handles bpy mocking
from blender_addon.application.handlers.scene import SceneHandler

class TestSceneConstruction:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = SceneHandler()
        # Reset mocks
        self.mock_bpy.data.lights.new = MagicMock()
        self.mock_bpy.data.cameras.new = MagicMock()
        self.mock_bpy.data.objects.new = MagicMock()
        self.mock_bpy.context.collection.objects.link = MagicMock()
        
    def test_create_light(self):
        # Setup
        light_data = MagicMock()
        self.mock_bpy.data.lights.new.return_value = light_data
        
        light_obj = MagicMock()
        light_obj.name = "MyLight"
        self.mock_bpy.data.objects.new.return_value = light_obj
        
        # Execute
        result = self.handler.create_light(
            type='SPOT', 
            energy=500.0, 
            color=[1.0, 0.0, 0.0], 
            location=[1, 2, 3], 
            name="MyLight"
        )
        
        # Verify
        self.mock_bpy.data.lights.new.assert_called_with(name="MyLight", type='SPOT')
        assert light_data.energy == 500.0
        assert light_data.color == [1.0, 0.0, 0.0]
        
        self.mock_bpy.data.objects.new.assert_called_with(name="MyLight", object_data=light_data)
        assert light_obj.location == [1, 2, 3]
        
        self.mock_bpy.context.collection.objects.link.assert_called_with(light_obj)
        assert result == "MyLight"

    def test_create_camera(self):
        # Setup
        cam_data = MagicMock()
        self.mock_bpy.data.cameras.new.return_value = cam_data
        
        cam_obj = MagicMock()
        cam_obj.name = "ShotCam"
        self.mock_bpy.data.objects.new.return_value = cam_obj
        
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
        self.mock_bpy.data.cameras.new.assert_called_with(name="ShotCam")
        assert cam_data.lens == 85.0
        assert cam_data.clip_start == 0.5
        assert cam_data.clip_end == 200.0
        
        self.mock_bpy.data.objects.new.assert_called_with(name="ShotCam", object_data=cam_data)
        assert cam_obj.location == [0, -5, 1]
        assert cam_obj.rotation_euler == [1.5, 0, 0]
        
        self.mock_bpy.context.collection.objects.link.assert_called_with(cam_obj)
        assert result == "ShotCam"

    def test_create_empty(self):
        # Setup
        empty_obj = MagicMock()
        empty_obj.name = "Controller"
        self.mock_bpy.data.objects.new.return_value = empty_obj
        
        # Execute
        result = self.handler.create_empty(
            type='CUBE',
            size=0.5,
            location=[1, 1, 1],
            name="Controller"
        )
        
        # Verify
        self.mock_bpy.data.objects.new.assert_called_with("Controller", None)
        assert empty_obj.empty_display_type == 'CUBE'
        assert empty_obj.empty_display_size == 0.5
        assert empty_obj.location == [1, 1, 1]
        
        self.mock_bpy.context.collection.objects.link.assert_called_with(empty_obj)
        assert result == "Controller"

