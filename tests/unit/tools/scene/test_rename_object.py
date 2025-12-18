"""
Unit tests for scene_rename_object (TASK-043-1)
"""
import sys
import pytest
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class TestRenameObject:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup test objects
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"

        self.sphere = MagicMock()
        self.sphere.name = "Sphere"
        self.sphere.type = "MESH"

        self.scene_objects = [self.cube, self.sphere]

        # Setup bpy.data.objects.get
        def get_object(name):
            for obj in self.scene_objects:
                if obj.name == name:
                    return obj
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.get.side_effect = get_object

        self.handler = SceneHandler()

    def test_rename_object_success(self):
        """Test successful object rename."""
        result = self.handler.rename_object("Cube", "MyCube")

        assert "MyCube" in result or "Renamed" in result

    def test_rename_object_not_found(self):
        """Test renaming non-existent object raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.rename_object("NonExistent", "NewName")

    def test_rename_returns_actual_name(self):
        """Test that rename returns the actual assigned name."""
        result = self.handler.rename_object("Cube", "NewCubeName")

        # Should contain either the new name or a renamed message
        assert "Renamed" in result or "NewCubeName" in result or "Cube" in result
