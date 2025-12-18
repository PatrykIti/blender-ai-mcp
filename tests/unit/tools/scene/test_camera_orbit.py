"""
Unit tests for scene_camera_orbit (TASK-043-5)
"""
import sys
import pytest
from unittest.mock import MagicMock, patch

from blender_addon.application.handlers.scene import SceneHandler


class TestCameraOrbit:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup test object for target
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.location = MagicMock()
        self.cube.location.copy.return_value = MagicMock()

        # Setup bpy.data.objects.get
        def get_object(name):
            if name == "Cube":
                return self.cube
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.get.side_effect = get_object

        # Setup 3D view area
        self.rv3d = MagicMock()
        self.rv3d.view_rotation = MagicMock()
        self.rv3d.view_location = MagicMock()

        self.space = MagicMock()
        self.space.region_3d = self.rv3d

        self.region = MagicMock()
        self.region.type = 'WINDOW'

        self.area = MagicMock()
        self.area.type = 'VIEW_3D'
        self.area.regions = [self.region]
        self.area.spaces = [self.space]

        self.mock_bpy.context.screen.areas = [self.area]

        self.handler = SceneHandler()

    def test_camera_orbit_horizontal(self):
        """Test horizontal orbit rotation."""
        result = self.handler.camera_orbit(
            angle_horizontal=45.0,
            angle_vertical=0.0
        )

        assert "orbit" in result.lower() or "rotated" in result.lower() or "45" in result

    def test_camera_orbit_vertical(self):
        """Test vertical orbit rotation."""
        result = self.handler.camera_orbit(
            angle_horizontal=0.0,
            angle_vertical=30.0
        )

        assert "orbit" in result.lower() or "rotated" in result.lower() or "30" in result

    def test_camera_orbit_with_target_object(self):
        """Test orbit around target object."""
        result = self.handler.camera_orbit(
            angle_horizontal=90.0,
            angle_vertical=0.0,
            target_object="Cube"
        )

        assert "Cube" in result or "orbit" in result.lower()

    def test_camera_orbit_with_target_point(self):
        """Test orbit around specific point."""
        result = self.handler.camera_orbit(
            angle_horizontal=45.0,
            angle_vertical=45.0,
            target_point=[1.0, 2.0, 3.0]
        )

        assert "orbit" in result.lower() or "rotated" in result.lower()

    def test_camera_orbit_target_not_found(self):
        """Test orbit with non-existent target object."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.camera_orbit(
                angle_horizontal=45.0,
                target_object="NonExistent"
            )
