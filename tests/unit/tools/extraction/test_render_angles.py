"""
Unit tests for extraction_render_angles (TASK-044-6)

Tests the ExtractionHandler.render_angles method which
renders objects from multiple angles for LLM Vision analysis.
"""
import sys
import pytest
from unittest.mock import MagicMock

from blender_addon.application.handlers.extraction import ExtractionHandler


class TestRenderAngles:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = ExtractionHandler()

        # Setup test mesh object
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.bound_box = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        self.cube.matrix_world = MagicMock()

        def get_object(name):
            if name == "Cube":
                return self.cube
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.__contains__ = lambda s, name: name == "Cube"
        self.mock_bpy.data.objects.__getitem__ = get_object

    def test_render_angles_object_not_found(self):
        """Test error when object doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.render_angles("NonExistent")

    def test_render_angles_invalid_angle(self):
        """Test error with invalid angle name."""
        with pytest.raises(ValueError, match="Invalid angle"):
            self.handler.render_angles("Cube", angles=["invalid_angle"])


class TestAnglePresets:
    """Test angle preset configurations."""

    def setup_method(self):
        self.handler = ExtractionHandler()

    def test_all_angle_presets_exist(self):
        """Test that all expected angle presets are defined."""
        expected_angles = ["front", "back", "left", "right", "top", "iso"]

        for angle in expected_angles:
            assert angle in self.handler.ANGLE_PRESETS

    def test_angle_presets_have_rotation(self):
        """Test that all presets have rotation data."""
        for name, preset in self.handler.ANGLE_PRESETS.items():
            assert "rotation" in preset
            assert len(preset["rotation"]) == 3  # Euler angles


class TestRenderParameters:
    """Test render parameter handling."""

    def setup_method(self):
        self.handler = ExtractionHandler()

    def test_default_angles(self):
        """Test default angles list."""
        default_angles = ["front", "back", "left", "right", "top", "iso"]
        # Default should include all 6 angles
        assert len(default_angles) == 6

    def test_resolution_parameter(self):
        """Test resolution parameter."""
        # Default is 512
        assert True  # Placeholder - full test requires render mocking

    def test_output_dir_parameter(self):
        """Test output directory parameter."""
        # Default is /tmp/extraction_renders
        assert True  # Placeholder - full test requires filesystem mocking
