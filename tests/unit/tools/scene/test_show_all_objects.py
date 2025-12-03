"""
Unit tests for scene_show_all_objects (TASK-043-3)
"""
import sys
import pytest
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class TestShowAllObjects:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup test objects - some hidden, some visible
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.hide_viewport = True
        self.cube.hide_render = True

        self.sphere = MagicMock()
        self.sphere.name = "Sphere"
        self.sphere.hide_viewport = True
        self.sphere.hide_render = False

        self.camera = MagicMock()
        self.camera.name = "Camera"
        self.camera.hide_viewport = False
        self.camera.hide_render = False

        self.scene_objects = [self.cube, self.sphere, self.camera]

        # Setup bpy.data.objects iteration
        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.__iter__ = lambda s: iter(self.scene_objects)

        self.handler = SceneHandler()

    def test_show_all_objects_viewport_only(self):
        """Test showing all objects in viewport only."""
        result = self.handler.show_all_objects(include_render=False)

        # All objects should be visible in viewport
        assert self.cube.hide_viewport == False
        assert self.sphere.hide_viewport == False
        assert self.camera.hide_viewport == False

        # Render visibility should NOT change
        assert self.cube.hide_render == True  # Was hidden, stays hidden in render

        assert "2" in result  # 2 objects were unhidden

    def test_show_all_objects_include_render(self):
        """Test showing all objects in viewport and render."""
        result = self.handler.show_all_objects(include_render=True)

        # All objects should be visible everywhere
        assert self.cube.hide_viewport == False
        assert self.sphere.hide_viewport == False
        assert self.cube.hide_render == False
        assert self.sphere.hide_render == False

    def test_show_all_objects_none_hidden(self):
        """Test when no objects are hidden."""
        self.cube.hide_viewport = False
        self.sphere.hide_viewport = False

        result = self.handler.show_all_objects(include_render=False)

        assert "0" in result  # 0 objects were unhidden
