"""
Unit tests for scene_camera_focus (TASK-043-6)
"""
import sys
import pytest
from unittest.mock import MagicMock, patch

from blender_addon.application.handlers.scene import SceneHandler


class TestCameraFocus:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup test object
        self.cube = MagicMock()
        self.cube.name = "Cube"

        # Setup bpy.data.objects.get
        def get_object(name):
            if name == "Cube":
                return self.cube
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.get.side_effect = get_object

        # Setup view layer
        self.mock_bpy.context.view_layer.objects.active = None

        # Setup 3D view area with proper space type
        self.rv3d = MagicMock()
        self.rv3d.view_distance = 10.0

        self.space = MagicMock()
        self.space.type = 'VIEW_3D'
        self.space.region_3d = self.rv3d

        self.region = MagicMock()
        self.region.type = 'WINDOW'

        self.area = MagicMock()
        self.area.type = 'VIEW_3D'
        self.area.spaces = [self.space]
        self.area.regions = [self.region]

        self.mock_bpy.context.screen.areas = [self.area]

        # Setup operators
        self.mock_bpy.ops.object.select_all = MagicMock()
        self.mock_bpy.ops.view3d.view_selected = MagicMock()

        # Setup temp_override context manager
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=None)
        mock_context_manager.__exit__ = MagicMock(return_value=False)
        self.mock_bpy.context.temp_override = MagicMock(return_value=mock_context_manager)

        self.handler = SceneHandler()

    def test_camera_focus_success(self):
        """Test focusing on object."""
        result = self.handler.camera_focus("Cube", zoom_factor=1.0)

        # Should return success message
        assert "Focused" in result or "Cube" in result

    def test_camera_focus_zoom_in(self):
        """Test focus with zoom in."""
        result = self.handler.camera_focus("Cube", zoom_factor=2.0)

        # Should mention focus and zoom
        assert "Cube" in result or "focus" in result.lower()

    def test_camera_focus_zoom_out(self):
        """Test focus with zoom out."""
        result = self.handler.camera_focus("Cube", zoom_factor=0.5)

        # Should mention focus
        assert "Cube" in result or "focus" in result.lower()

    def test_camera_focus_not_found(self):
        """Test focus on non-existent object."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.camera_focus("NonExistent")

    def test_camera_focus_calls_operators(self):
        """Test that focus calls necessary operators."""
        self.handler.camera_focus("Cube", zoom_factor=1.0)

        # Should deselect all first
        self.mock_bpy.ops.object.select_all.assert_called_with(action='DESELECT')

        # Should select the target object
        self.cube.select_set.assert_called_with(True)
