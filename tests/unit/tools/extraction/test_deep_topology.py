"""
Unit tests for extraction_deep_topology (TASK-044-1)

Tests the ExtractionHandler.deep_topology method which performs
extended topology analysis on mesh objects.
"""
import sys
import pytest
from unittest.mock import MagicMock, patch

from blender_addon.application.handlers.extraction import ExtractionHandler


class TestDeepTopology:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = ExtractionHandler()

        # Setup test mesh object
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.dimensions = MagicMock()
        self.cube.dimensions.x = 2.0
        self.cube.dimensions.y = 2.0
        self.cube.dimensions.z = 2.0
        self.cube.data = MagicMock()
        self.cube.matrix_world = MagicMock()
        self.cube.bound_box = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]

        def get_object(name):
            if name == "Cube":
                return self.cube
            return None

        self.mock_bpy.data.objects = MagicMock()
        self.mock_bpy.data.objects.__contains__ = lambda s, name: name == "Cube"
        self.mock_bpy.data.objects.__getitem__ = get_object

    def test_deep_topology_object_not_found(self):
        """Test error when object doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.deep_topology("NonExistent")

    def test_deep_topology_not_mesh(self):
        """Test error when object is not a mesh."""
        camera = MagicMock()
        camera.name = "Camera"
        camera.type = "CAMERA"

        self.mock_bpy.data.objects.__contains__ = lambda s, name: name in ["Cube", "Camera"]
        self.mock_bpy.data.objects.__getitem__ = lambda s, name: camera if name == "Camera" else self.cube

        with pytest.raises(ValueError, match="not a mesh"):
            self.handler.deep_topology("Camera")


class TestBasePrimitiveDetection:
    """Test base primitive detection heuristics."""

    def setup_method(self):
        self.handler = ExtractionHandler()

    def test_detect_cube_shape(self):
        """Test cube detection with 8 vertices, 6 faces."""
        bm = MagicMock()
        obj = MagicMock()
        obj.dimensions.x = 2.0
        obj.dimensions.y = 2.0
        obj.dimensions.z = 2.0

        primitive, confidence = self.handler._detect_base_primitive(bm, 8, 12, 6, obj)

        assert primitive == "CUBE"
        assert confidence >= 0.7

    def test_detect_plane_shape(self):
        """Test plane detection with 4 vertices, 1 face."""
        bm = MagicMock()
        obj = MagicMock()
        obj.dimensions.x = 2.0
        obj.dimensions.y = 2.0
        obj.dimensions.z = 0.0

        primitive, confidence = self.handler._detect_base_primitive(bm, 4, 4, 1, obj)

        assert primitive == "PLANE"
        assert confidence >= 0.9

    def test_detect_custom_when_zero_dimensions(self):
        """Test custom detection when dimensions are zero."""
        bm = MagicMock()
        obj = MagicMock()
        obj.dimensions.x = 0.0
        obj.dimensions.y = 0.0
        obj.dimensions.z = 0.0

        primitive, confidence = self.handler._detect_base_primitive(bm, 100, 200, 50, obj)

        assert primitive == "CUSTOM"
        assert confidence == 0.0
