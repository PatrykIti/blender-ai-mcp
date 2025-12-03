"""
Unit tests for scene_camera_focus (TASK-043-6)

NOTE: Complex viewport manipulation with mathutils.Vector is difficult to mock.
Full functionality is tested in E2E tests with real Blender.
Unit tests focus on error handling and basic flow.
"""
import sys
import pytest
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class TestCameraFocus:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup test objects
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.data = MagicMock()

        self.camera = MagicMock()
        self.camera.name = "Camera"
        self.camera.type = "CAMERA"
        self.camera.data = None  # Non-mesh object
        self.camera.location = MagicMock()
        self.camera.location.copy = MagicMock(return_value=MagicMock())

        # Setup bpy.data.objects.get
        def get_object(name):
            if name == "Cube":
                return self.cube
            if name == "Camera":
                return self.camera
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.get.side_effect = get_object

        # Setup view layer
        self.mock_bpy.context.view_layer.objects.active = None

        # Setup 3D view area
        self.rv3d = MagicMock()
        self.rv3d.view_distance = 10.0
        self.rv3d.view_location = MagicMock()

        self.space = MagicMock()
        self.space.type = 'VIEW_3D'
        self.space.region_3d = self.rv3d

        self.area = MagicMock()
        self.area.type = 'VIEW_3D'
        self.area.spaces = [self.space]

        self.mock_bpy.context.screen.areas = [self.area]

        self.handler = SceneHandler()

    def test_camera_focus_not_found(self):
        """Test focus on non-existent object."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.camera_focus("NonExistent")

    def test_camera_focus_no_viewport(self):
        """Test focus when no viewport is available."""
        self.mock_bpy.context.screen.areas = []  # No areas

        result = self.handler.camera_focus("Cube", zoom_factor=1.0)

        assert "No 3D viewport" in result

    def test_camera_focus_non_mesh_object(self):
        """Test focus on non-mesh object (uses location fallback)."""
        # Camera has no mesh data, so it uses location.copy() fallback
        result = self.handler.camera_focus("Camera", zoom_factor=1.0)

        # Should succeed with fallback to object location
        assert "Focused" in result or "Camera" in result

    def test_camera_focus_sets_active_object(self):
        """Test that focus sets the object as active."""
        self.handler.camera_focus("Camera", zoom_factor=1.0)

        # Should set active object
        assert self.mock_bpy.context.view_layer.objects.active == self.camera

    def test_camera_focus_selects_object(self):
        """Test that focus selects the object."""
        self.handler.camera_focus("Camera", zoom_factor=1.0)

        # Should select the target object
        self.camera.select_set.assert_called_with(True)
