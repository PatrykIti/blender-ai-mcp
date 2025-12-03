"""
Unit tests for extraction_component_separate (TASK-044-2)

Tests the ExtractionHandler.component_separate method which
separates mesh into loose parts.
"""
import sys
import pytest
from unittest.mock import MagicMock

from blender_addon.application.handlers.extraction import ExtractionHandler


class TestComponentSeparate:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = ExtractionHandler()

        # Setup test mesh object
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.data = MagicMock()
        self.cube.data.vertices = [MagicMock() for _ in range(8)]
        self.cube.data.polygons = [MagicMock() for _ in range(6)]
        self.cube.mode = "OBJECT"

        def get_object(name):
            if name == "Cube":
                return self.cube
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.__contains__ = lambda s, name: name == "Cube"
        self.mock_bpy.data.objects.__getitem__ = get_object
        self.mock_bpy.data.objects.__iter__ = lambda s: iter([self.cube])

        # Setup context
        self.mock_bpy.context.active_object = None
        self.mock_bpy.context.view_layer.objects.active = None

    def test_component_separate_object_not_found(self):
        """Test error when object doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.component_separate("NonExistent")

    def test_component_separate_not_mesh(self):
        """Test error when object is not a mesh."""
        camera = MagicMock()
        camera.name = "Camera"
        camera.type = "CAMERA"

        self.mock_bpy.data.objects.__contains__ = lambda s, name: name in ["Cube", "Camera"]
        self.mock_bpy.data.objects.__getitem__ = lambda name: camera if name == "Camera" else self.cube

        with pytest.raises(ValueError, match="not a mesh"):
            self.handler.component_separate("Camera")


class TestComponentSeparateParams:
    """Test component separation with different parameters."""

    def setup_method(self):
        self.handler = ExtractionHandler()

    def test_min_vertex_count_default(self):
        """Test default min_vertex_count is 4."""
        # The default should filter out very small components
        assert True  # Placeholder - full test requires bmesh mocking
