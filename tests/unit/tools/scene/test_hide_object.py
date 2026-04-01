"""
Unit tests for scene_hide_object (TASK-043-2)
"""

import sys
from unittest.mock import MagicMock

import pytest
from blender_addon.application.handlers.scene import SceneHandler


class TestHideObject:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup test objects
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.hide_viewport = False
        self.cube.hide_render = False

        self.scene_objects = [self.cube]

        # Setup bpy.data.objects.get
        def get_object(name):
            for obj in self.scene_objects:
                if obj.name == name:
                    return obj
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.get.side_effect = get_object

        self.handler = SceneHandler()

    def test_hide_object_viewport(self):
        """Test hiding object in viewport."""
        result = self.handler.hide_object("Cube", hide=True, hide_render=False)

        assert self.cube.hide_viewport
        assert "hidden" in result.lower() or "Cube" in result

    def test_show_object_viewport(self):
        """Showing an object should restore both viewport and render visibility."""
        self.cube.hide_viewport = True
        self.cube.hide_render = True

        result = self.handler.hide_object("Cube", hide=False, hide_render=False)

        assert not self.cube.hide_viewport
        assert not self.cube.hide_render
        assert "visible" in result.lower() or "Cube" in result

    def test_hide_object_render(self):
        """Test hiding object in both viewport and render."""
        self.handler.hide_object("Cube", hide=True, hide_render=True)

        assert self.cube.hide_viewport
        assert self.cube.hide_render

    def test_show_object_reports_render_visibility_restore(self):
        """Show action should make the render-visibility side effect explicit."""

        self.cube.hide_viewport = True
        self.cube.hide_render = True

        result = self.handler.hide_object("Cube", hide=False, hide_render=False)

        assert "including render visibility" in result

    def test_hide_object_not_found(self):
        """Test hiding non-existent object raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.hide_object("NonExistent", hide=True)
