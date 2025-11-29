"""
Tests for TASK-027 (Sculpting Tools).
Pure pytest style - uses conftest.py fixtures.
"""
import pytest
from unittest.mock import MagicMock, patch

import bpy

from blender_addon.application.handlers.sculpt import SculptHandler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sculpt_handler():
    """Provides a fresh SculptHandler instance."""
    return SculptHandler()


@pytest.fixture
def mock_sculpt_tool_settings():
    """Sets up mock sculpt tool settings for Blender 5.0+ symmetry."""
    mock_sculpt = MagicMock()
    mock_sculpt.use_symmetry_x = False
    mock_sculpt.use_symmetry_y = False
    mock_sculpt.use_symmetry_z = False
    mock_sculpt.brush = MagicMock()
    mock_sculpt.brush.size = 50
    mock_sculpt.brush.strength = 0.5
    mock_sculpt.brush.crease_pinch_factor = 0.5

    mock_tool_settings = MagicMock()
    mock_tool_settings.sculpt = mock_sculpt

    mock_scene = MagicMock()
    mock_scene.tool_settings = mock_tool_settings

    bpy.context.scene = mock_scene
    bpy.context.tool_settings = mock_tool_settings
    return mock_sculpt


@pytest.fixture
def mock_mesh_object(mock_sculpt_tool_settings):
    """Sets up mock mesh object in object mode."""
    mock_obj = MagicMock()
    mock_obj.name = 'Cube'
    mock_obj.type = 'MESH'
    mock_obj.mode = 'OBJECT'
    bpy.context.active_object = mock_obj
    bpy.data.objects = {'Cube': mock_obj}
    return mock_obj


@pytest.fixture
def mock_mesh_object_sculpt_mode(mock_sculpt_tool_settings):
    """Sets up mock mesh object already in sculpt mode."""
    mock_obj = MagicMock()
    mock_obj.name = 'Sphere'
    mock_obj.type = 'MESH'
    mock_obj.mode = 'SCULPT'
    bpy.context.active_object = mock_obj
    bpy.data.objects = {'Sphere': mock_obj}
    return mock_obj


@pytest.fixture
def mock_sculpt_context(mock_sculpt_tool_settings):
    """Sets up mock sculpt context with brush (depends on mock_sculpt_tool_settings)."""
    return mock_sculpt_tool_settings


# =============================================================================
# TASK-027-1: sculpt_auto tests
# =============================================================================

class TestSculptAuto:
    """Tests for sculpt_auto tool (mesh filters)."""

    def test_auto_sculpt_smooth_default(self, sculpt_handler, mock_mesh_object):
        """Should apply smooth filter with default parameters."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        result = sculpt_handler.auto_sculpt()

        bpy.ops.object.mode_set.assert_called_with(mode='SCULPT')
        bpy.ops.sculpt.mesh_filter.assert_called_with(type='SMOOTH', strength=0.5)
        assert "smooth" in result.lower()
        assert "Cube" in result

    def test_auto_sculpt_inflate(self, sculpt_handler, mock_mesh_object_sculpt_mode):
        """Should apply inflate filter."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        result = sculpt_handler.auto_sculpt(operation="inflate", strength=0.3)

        bpy.ops.sculpt.mesh_filter.assert_called_with(type='INFLATE', strength=0.3)
        assert "inflate" in result.lower()

    def test_auto_sculpt_flatten(self, sculpt_handler, mock_mesh_object_sculpt_mode):
        """Should apply flatten filter (mapped to SURFACE_SMOOTH in Blender 5.0+)."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        result = sculpt_handler.auto_sculpt(operation="flatten")

        # FLATTEN was removed in Blender 5.0, mapped to SURFACE_SMOOTH
        bpy.ops.sculpt.mesh_filter.assert_called_with(type='SURFACE_SMOOTH', strength=0.5)
        assert "flatten" in result.lower()

    def test_auto_sculpt_sharpen(self, sculpt_handler, mock_mesh_object_sculpt_mode):
        """Should apply sharpen filter."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        result = sculpt_handler.auto_sculpt(operation="sharpen")

        bpy.ops.sculpt.mesh_filter.assert_called_with(type='SHARPEN', strength=0.5)
        assert "sharpen" in result.lower()

    def test_auto_sculpt_multiple_iterations(self, sculpt_handler, mock_mesh_object_sculpt_mode):
        """Should apply filter multiple times for iterations > 1."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        result = sculpt_handler.auto_sculpt(operation="smooth", iterations=5)

        assert bpy.ops.sculpt.mesh_filter.call_count == 5
        assert "5 iterations" in result

    def test_auto_sculpt_with_symmetry(self, sculpt_handler, mock_mesh_object):
        """Should enable symmetry on specified axis."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        result = sculpt_handler.auto_sculpt(use_symmetry=True, symmetry_axis="Y")

        # Blender 5.0+: symmetry is on sculpt tool settings
        sculpt_settings = bpy.context.scene.tool_settings.sculpt
        assert sculpt_settings.use_symmetry_y is True
        assert sculpt_settings.use_symmetry_x is False
        assert sculpt_settings.use_symmetry_z is False
        assert "symmetry: Y" in result

    def test_auto_sculpt_no_symmetry(self, sculpt_handler, mock_mesh_object):
        """Should not enable symmetry when use_symmetry=False."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        result = sculpt_handler.auto_sculpt(use_symmetry=False)

        # Blender 5.0+: symmetry is on sculpt tool settings
        sculpt_settings = bpy.context.scene.tool_settings.sculpt
        assert sculpt_settings.use_symmetry_x is False
        assert sculpt_settings.use_symmetry_y is False
        assert sculpt_settings.use_symmetry_z is False
        assert "symmetry" not in result

    def test_auto_sculpt_clamps_strength(self, sculpt_handler, mock_mesh_object_sculpt_mode):
        """Should clamp strength to 0-1 range."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.sculpt.mesh_filter = MagicMock()

        # Test value > 1
        sculpt_handler.auto_sculpt(strength=2.0)
        bpy.ops.sculpt.mesh_filter.assert_called_with(type='SMOOTH', strength=1.0)

        # Test value < 0
        sculpt_handler.auto_sculpt(strength=-0.5)
        bpy.ops.sculpt.mesh_filter.assert_called_with(type='SMOOTH', strength=0.0)

    def test_auto_sculpt_invalid_operation_raises(self, sculpt_handler, mock_mesh_object_sculpt_mode):
        """Should raise ValueError for invalid operation."""
        bpy.ops.object.mode_set = MagicMock()

        with pytest.raises(ValueError, match="Invalid operation"):
            sculpt_handler.auto_sculpt(operation="invalid_op")

    def test_auto_sculpt_object_not_found_raises(self, sculpt_handler):
        """Should raise ValueError when object not found."""
        bpy.data.objects = {}

        with pytest.raises(ValueError, match="not found"):
            sculpt_handler.auto_sculpt(object_name="NonExistent")

    def test_auto_sculpt_non_mesh_raises(self, sculpt_handler):
        """Should raise ValueError for non-mesh objects."""
        mock_camera = MagicMock()
        mock_camera.name = 'Camera'
        mock_camera.type = 'CAMERA'
        bpy.data.objects = {'Camera': mock_camera}
        bpy.context.view_layer = MagicMock()
        bpy.context.active_object = mock_camera

        with pytest.raises(ValueError, match="not a mesh"):
            sculpt_handler.auto_sculpt(object_name="Camera")


# =============================================================================
# TASK-027-2: sculpt_brush_smooth tests
# =============================================================================

class TestSculptBrushSmooth:
    """Tests for sculpt_brush_smooth tool."""

    def test_brush_smooth_sets_brush(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should set up smooth brush with correct parameters."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        result = sculpt_handler.brush_smooth(radius=0.15, strength=0.8)

        bpy.ops.wm.tool_set_by_id.assert_called_with(name="builtin_brush.Smooth")
        assert mock_sculpt_context.brush.strength == 0.8
        assert "Smooth brush ready" in result

    def test_brush_smooth_with_location(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should include location in result message."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        result = sculpt_handler.brush_smooth(location=[1.0, 2.0, 3.0])

        assert "[1.0, 2.0, 3.0]" in result

    def test_brush_smooth_clamps_values(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should clamp radius and strength to valid ranges."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        # Strength should be clamped to 1.0
        sculpt_handler.brush_smooth(strength=2.0)
        assert mock_sculpt_context.brush.strength == 1.0

        # Strength should be clamped to 0.0
        sculpt_handler.brush_smooth(strength=-0.5)
        assert mock_sculpt_context.brush.strength == 0.0


# =============================================================================
# TASK-027-3: sculpt_brush_grab tests
# =============================================================================

class TestSculptBrushGrab:
    """Tests for sculpt_brush_grab tool."""

    def test_brush_grab_sets_brush(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should set up grab brush with correct parameters."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        result = sculpt_handler.brush_grab(radius=0.2, strength=0.7)

        bpy.ops.wm.tool_set_by_id.assert_called_with(name="builtin_brush.Grab")
        assert mock_sculpt_context.brush.strength == 0.7
        assert "Grab brush ready" in result

    def test_brush_grab_with_locations(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should include from/to locations in result message."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        result = sculpt_handler.brush_grab(
            from_location=[0, 0, 0],
            to_location=[0, 0, 1]
        )

        assert "[0, 0, 0]" in result
        assert "[0, 0, 1]" in result


# =============================================================================
# TASK-027-4: sculpt_brush_crease tests
# =============================================================================

class TestSculptBrushCrease:
    """Tests for sculpt_brush_crease tool."""

    def test_brush_crease_sets_brush(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should set up crease brush with correct parameters."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        result = sculpt_handler.brush_crease(radius=0.05, strength=0.9, pinch=0.8)

        bpy.ops.wm.tool_set_by_id.assert_called_with(name="builtin_brush.Crease")
        assert mock_sculpt_context.brush.strength == 0.9
        assert mock_sculpt_context.brush.crease_pinch_factor == 0.8
        assert "Crease brush ready" in result

    def test_brush_crease_with_location(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should include location in result message."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        result = sculpt_handler.brush_crease(location=[0.5, 0.5, 2.0])

        assert "[0.5, 0.5, 2.0]" in result

    def test_brush_crease_clamps_pinch(self, sculpt_handler, mock_mesh_object, mock_sculpt_context):
        """Should clamp pinch to 0-1 range."""
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.wm.tool_set_by_id = MagicMock()

        # Pinch should be clamped to 1.0
        sculpt_handler.brush_crease(pinch=1.5)
        assert mock_sculpt_context.brush.crease_pinch_factor == 1.0

        # Pinch should be clamped to 0.0
        sculpt_handler.brush_crease(pinch=-0.3)
        assert mock_sculpt_context.brush.crease_pinch_factor == 0.0


# =============================================================================
# Helper function tests
# =============================================================================

class TestSculptHelpers:
    """Tests for helper methods."""

    def test_ensure_sculpt_mode_switches_mode(self, sculpt_handler, mock_mesh_object):
        """Should switch to sculpt mode if not already in it."""
        bpy.ops.object.mode_set = MagicMock()

        obj, prev_mode = sculpt_handler._ensure_sculpt_mode()

        bpy.ops.object.mode_set.assert_called_with(mode='SCULPT')
        assert prev_mode == 'OBJECT'

    def test_ensure_sculpt_mode_stays_in_sculpt(self, sculpt_handler, mock_mesh_object_sculpt_mode):
        """Should not switch mode if already in sculpt mode."""
        bpy.ops.object.mode_set = MagicMock()

        obj, prev_mode = sculpt_handler._ensure_sculpt_mode()

        # Should not be called since already in SCULPT mode
        bpy.ops.object.mode_set.assert_not_called()
        assert prev_mode == 'SCULPT'

    def test_set_symmetry_x(self, sculpt_handler, mock_mesh_object):
        """Should set X symmetry correctly (Blender 5.0+ uses sculpt tool settings)."""
        sculpt_handler._set_symmetry(mock_mesh_object, True, 'X')

        # Blender 5.0+: symmetry is on sculpt tool settings, not on object
        sculpt_settings = bpy.context.scene.tool_settings.sculpt
        assert sculpt_settings.use_symmetry_x is True
        assert sculpt_settings.use_symmetry_y is False
        assert sculpt_settings.use_symmetry_z is False

    def test_set_symmetry_y(self, sculpt_handler, mock_mesh_object):
        """Should set Y symmetry correctly (Blender 5.0+ uses sculpt tool settings)."""
        sculpt_handler._set_symmetry(mock_mesh_object, True, 'Y')

        sculpt_settings = bpy.context.scene.tool_settings.sculpt
        assert sculpt_settings.use_symmetry_x is False
        assert sculpt_settings.use_symmetry_y is True
        assert sculpt_settings.use_symmetry_z is False

    def test_set_symmetry_z(self, sculpt_handler, mock_mesh_object):
        """Should set Z symmetry correctly (Blender 5.0+ uses sculpt tool settings)."""
        sculpt_handler._set_symmetry(mock_mesh_object, True, 'Z')

        sculpt_settings = bpy.context.scene.tool_settings.sculpt
        assert sculpt_settings.use_symmetry_x is False
        assert sculpt_settings.use_symmetry_y is False
        assert sculpt_settings.use_symmetry_z is True

    def test_set_symmetry_disabled(self, sculpt_handler, mock_mesh_object):
        """Should disable all symmetry when use_symmetry=False."""
        # First enable X symmetry
        sculpt_settings = bpy.context.scene.tool_settings.sculpt
        sculpt_settings.use_symmetry_x = True

        sculpt_handler._set_symmetry(mock_mesh_object, False, 'X')

        assert sculpt_settings.use_symmetry_x is False
        assert sculpt_settings.use_symmetry_y is False
        assert sculpt_settings.use_symmetry_z is False
