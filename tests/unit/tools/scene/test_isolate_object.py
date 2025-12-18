"""
Unit tests for scene_isolate_object (TASK-043-4)
"""
import sys
import pytest
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class TestIsolateObject:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup test objects
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.hide_viewport = False

        self.sphere = MagicMock()
        self.sphere.name = "Sphere"
        self.sphere.hide_viewport = False

        self.camera = MagicMock()
        self.camera.name = "Camera"
        self.camera.hide_viewport = False

        self.light = MagicMock()
        self.light.name = "Light"
        self.light.hide_viewport = False

        self.scene_objects = [self.cube, self.sphere, self.camera, self.light]
        self.object_names = {obj.name for obj in self.scene_objects}

        # Setup bpy.data.objects - needs both iteration and __contains__
        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.__iter__ = lambda s: iter(self.scene_objects)
        self.mock_bpy.data.objects.__contains__ = lambda s, name: name in self.object_names

        self.handler = SceneHandler()

    def test_isolate_single_object(self):
        """Test isolating a single object."""
        result = self.handler.isolate_object(["Cube"])

        # Cube should be visible
        assert self.cube.hide_viewport == False

        # All others should be hidden
        assert self.sphere.hide_viewport == True
        assert self.camera.hide_viewport == True
        assert self.light.hide_viewport == True

        assert "3" in result  # 3 objects hidden

    def test_isolate_multiple_objects(self):
        """Test isolating multiple objects."""
        result = self.handler.isolate_object(["Cube", "Sphere"])

        # Cube and Sphere should be visible
        assert self.cube.hide_viewport == False
        assert self.sphere.hide_viewport == False

        # Others should be hidden
        assert self.camera.hide_viewport == True
        assert self.light.hide_viewport == True

        assert "2" in result  # 2 objects hidden

    def test_isolate_all_objects(self):
        """Test isolating all objects (nothing hidden)."""
        result = self.handler.isolate_object(["Cube", "Sphere", "Camera", "Light"])

        # All should be visible
        assert self.cube.hide_viewport == False
        assert self.sphere.hide_viewport == False
        assert self.camera.hide_viewport == False
        assert self.light.hide_viewport == False

        assert "0" in result  # 0 objects hidden

    def test_isolate_unhides_target(self):
        """Test that isolate unhides the target object if it was hidden."""
        self.cube.hide_viewport = True  # Target is initially hidden

        result = self.handler.isolate_object(["Cube"])

        # Target should now be visible
        assert self.cube.hide_viewport == False

    def test_isolate_object_not_found(self):
        """Test isolating non-existent object raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.isolate_object(["NonExistent"])
