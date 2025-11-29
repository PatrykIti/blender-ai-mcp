"""
Tests for TASK-021 (Phase 2.6 - Curves & Procedural) curve tools.
Pure pytest style - uses conftest.py fixtures.
"""
import pytest
from unittest.mock import MagicMock

import bpy

from blender_addon.application.handlers.curve import CurveHandler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def curve_handler():
    """Provides a fresh CurveHandler instance."""
    return CurveHandler()


@pytest.fixture
def mock_curve_object():
    """Sets up mock curve object."""
    mock_obj = MagicMock()
    mock_obj.name = 'BezierCurve'
    mock_obj.type = 'CURVE'
    bpy.context.active_object = mock_obj
    return mock_obj


@pytest.fixture
def mock_mesh_object():
    """Sets up mock mesh object."""
    mock_obj = MagicMock()
    mock_obj.name = 'Cube'
    mock_obj.type = 'MESH'
    bpy.context.active_object = mock_obj
    return mock_obj


# =============================================================================
# TASK-021-1: curve_create tests
# =============================================================================

class TestCurveCreate:
    """Tests for curve_create tool."""

    def test_create_bezier_default(self, curve_handler, mock_curve_object):
        """Should create Bezier curve at default location."""
        bpy.ops.curve.primitive_bezier_curve_add = MagicMock()

        result = curve_handler.create_curve()

        bpy.ops.curve.primitive_bezier_curve_add.assert_called_with(location=(0, 0, 0))
        assert "Created BEZIER curve" in result

    def test_create_bezier_with_location(self, curve_handler, mock_curve_object):
        """Should create Bezier curve at specified location."""
        bpy.ops.curve.primitive_bezier_curve_add = MagicMock()

        result = curve_handler.create_curve(curve_type='BEZIER', location=[1, 2, 3])

        bpy.ops.curve.primitive_bezier_curve_add.assert_called_with(location=(1, 2, 3))
        assert "[1, 2, 3]" in result

    def test_create_nurbs_curve(self, curve_handler, mock_curve_object):
        """Should create NURBS curve."""
        bpy.ops.curve.primitive_nurbs_curve_add = MagicMock()

        result = curve_handler.create_curve(curve_type='NURBS')

        bpy.ops.curve.primitive_nurbs_curve_add.assert_called_with(location=(0, 0, 0))
        assert "Created NURBS curve" in result

    def test_create_path(self, curve_handler, mock_curve_object):
        """Should create NURBS path."""
        bpy.ops.curve.primitive_nurbs_path_add = MagicMock()

        result = curve_handler.create_curve(curve_type='PATH')

        bpy.ops.curve.primitive_nurbs_path_add.assert_called_with(location=(0, 0, 0))
        assert "Created PATH curve" in result

    def test_create_circle(self, curve_handler, mock_curve_object):
        """Should create Bezier circle."""
        bpy.ops.curve.primitive_bezier_circle_add = MagicMock()

        result = curve_handler.create_curve(curve_type='CIRCLE')

        bpy.ops.curve.primitive_bezier_circle_add.assert_called_with(location=(0, 0, 0))
        assert "Created CIRCLE curve" in result

    def test_create_invalid_type_raises(self, curve_handler):
        """Should raise ValueError for invalid curve type."""
        with pytest.raises(ValueError, match="Invalid curve_type"):
            curve_handler.create_curve(curve_type='INVALID')

    def test_create_case_insensitive(self, curve_handler, mock_curve_object):
        """Should handle case-insensitive curve types."""
        bpy.ops.curve.primitive_bezier_curve_add = MagicMock()

        result = curve_handler.create_curve(curve_type='bezier')

        bpy.ops.curve.primitive_bezier_curve_add.assert_called()
        assert "BEZIER" in result


# =============================================================================
# TASK-021-2: curve_to_mesh tests
# =============================================================================

class TestCurveToMesh:
    """Tests for curve_to_mesh tool."""

    def test_convert_curve_to_mesh(self, curve_handler):
        """Should convert curve to mesh."""
        mock_obj = MagicMock()
        mock_obj.name = 'BezierCurve'
        mock_obj.type = 'CURVE'
        bpy.data.objects = {'BezierCurve': mock_obj}
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.convert = MagicMock()
        bpy.context.view_layer = MagicMock()
        bpy.context.active_object = mock_obj

        result = curve_handler.curve_to_mesh('BezierCurve')

        bpy.ops.object.convert.assert_called_with(target='MESH')
        assert "Converted CURVE" in result
        assert "to MESH" in result

    def test_convert_surface_to_mesh(self, curve_handler):
        """Should convert surface to mesh."""
        mock_obj = MagicMock()
        mock_obj.name = 'NurbsSurface'
        mock_obj.type = 'SURFACE'
        bpy.data.objects = {'NurbsSurface': mock_obj}
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.convert = MagicMock()
        bpy.context.view_layer = MagicMock()
        bpy.context.active_object = mock_obj

        result = curve_handler.curve_to_mesh('NurbsSurface')

        bpy.ops.object.convert.assert_called_with(target='MESH')
        assert "SURFACE" in result

    def test_convert_object_not_found_raises(self, curve_handler):
        """Should raise ValueError when object not found."""
        bpy.data.objects = {}

        with pytest.raises(ValueError, match="not found"):
            curve_handler.curve_to_mesh('NonExistent')

    def test_convert_mesh_raises(self, curve_handler, mock_mesh_object):
        """Should raise ValueError when object is already a mesh."""
        bpy.data.objects = {'Cube': mock_mesh_object}

        with pytest.raises(ValueError, match="not a CURVE"):
            curve_handler.curve_to_mesh('Cube')

    def test_convert_font_to_mesh(self, curve_handler):
        """Should convert text/font to mesh."""
        mock_obj = MagicMock()
        mock_obj.name = 'Text'
        mock_obj.type = 'FONT'
        bpy.data.objects = {'Text': mock_obj}
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.convert = MagicMock()
        bpy.context.view_layer = MagicMock()
        bpy.context.active_object = mock_obj

        result = curve_handler.curve_to_mesh('Text')

        bpy.ops.object.convert.assert_called_with(target='MESH')
        assert "FONT" in result
