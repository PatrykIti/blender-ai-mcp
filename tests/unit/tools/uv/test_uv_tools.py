"""
Unit tests for UV Tools (TASK-024)
Tests UVHandler methods with mocked bpy module.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import math

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()

import bpy

from blender_addon.application.handlers.uv import UVHandler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def uv_handler():
    """Provides a fresh UVHandler instance."""
    return UVHandler()


@pytest.fixture
def mock_mesh_object():
    """Sets up a mock mesh object for UV operations."""
    mock_obj = MagicMock()
    mock_obj.name = "TestMesh"
    mock_obj.type = 'MESH'
    mock_obj.mode = 'OBJECT'
    mock_obj.data.uv_layers = [MagicMock(name="UVMap")]

    # Setup bpy.data.objects as MagicMock
    mock_objects = MagicMock()
    mock_objects.__contains__ = MagicMock(return_value=True)
    mock_objects.__getitem__ = MagicMock(return_value=mock_obj)
    mock_objects.get = MagicMock(return_value=mock_obj)
    bpy.data.objects = mock_objects

    # Setup bpy.context
    bpy.context.active_object = mock_obj
    bpy.context.view_layer.objects.active = mock_obj
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)

    # Reset ops mocks
    bpy.ops.object.mode_set = MagicMock()
    bpy.ops.uv.smart_project = MagicMock()
    bpy.ops.uv.cube_project = MagicMock()
    bpy.ops.uv.cylinder_project = MagicMock()
    bpy.ops.uv.sphere_project = MagicMock()
    bpy.ops.uv.unwrap = MagicMock()
    bpy.ops.uv.select_all = MagicMock()
    bpy.ops.uv.pack_islands = MagicMock()
    bpy.ops.mesh.mark_seam = MagicMock()

    return mock_obj


@pytest.fixture
def mock_no_active_object():
    """Sets up context with no active object."""
    mock_objects = MagicMock()
    mock_objects.__contains__ = MagicMock(return_value=False)
    bpy.data.objects = mock_objects
    bpy.context.active_object = None
    return None


# =============================================================================
# uv_unwrap Tests
# =============================================================================

class TestUVUnwrap:
    """Tests for uv_unwrap functionality."""

    def test_unwrap_smart_project_default(self, uv_handler, mock_mesh_object):
        """Test SMART_PROJECT unwrap with default parameters."""
        result = uv_handler.unwrap(object_name="TestMesh")

        bpy.ops.uv.smart_project.assert_called_once_with(
            angle_limit=math.radians(66.0),
            island_margin=0.02,
            scale_to_bounds=True
        )
        assert "TestMesh" in result
        assert "SMART_PROJECT" in result

    def test_unwrap_smart_project_custom_params(self, uv_handler, mock_mesh_object):
        """Test SMART_PROJECT unwrap with custom parameters."""
        result = uv_handler.unwrap(
            object_name="TestMesh",
            method="SMART_PROJECT",
            angle_limit=45.0,
            island_margin=0.05,
            scale_to_bounds=False
        )

        bpy.ops.uv.smart_project.assert_called_once_with(
            angle_limit=math.radians(45.0),
            island_margin=0.05,
            scale_to_bounds=False
        )

    def test_unwrap_cube_project(self, uv_handler, mock_mesh_object):
        """Test CUBE projection unwrap."""
        result = uv_handler.unwrap(object_name="TestMesh", method="CUBE")

        bpy.ops.uv.cube_project.assert_called_once_with(scale_to_bounds=True)
        assert "CUBE" in result

    def test_unwrap_cylinder_project(self, uv_handler, mock_mesh_object):
        """Test CYLINDER projection unwrap."""
        result = uv_handler.unwrap(object_name="TestMesh", method="CYLINDER")

        bpy.ops.uv.cylinder_project.assert_called_once_with(scale_to_bounds=True)
        assert "CYLINDER" in result

    def test_unwrap_sphere_project(self, uv_handler, mock_mesh_object):
        """Test SPHERE projection unwrap."""
        result = uv_handler.unwrap(object_name="TestMesh", method="SPHERE")

        bpy.ops.uv.sphere_project.assert_called_once_with(scale_to_bounds=True)
        assert "SPHERE" in result

    def test_unwrap_standard(self, uv_handler, mock_mesh_object):
        """Test standard UNWRAP method."""
        result = uv_handler.unwrap(object_name="TestMesh", method="UNWRAP")

        bpy.ops.uv.unwrap.assert_called_once_with(
            method='ANGLE_BASED',
            margin=0.02
        )
        assert "UNWRAP" in result

    def test_unwrap_sets_edit_mode(self, uv_handler, mock_mesh_object):
        """Test that unwrap enters Edit mode if not already in it."""
        mock_mesh_object.mode = 'OBJECT'

        uv_handler.unwrap(object_name="TestMesh")

        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')

    def test_unwrap_object_not_found(self, uv_handler, mock_no_active_object):
        """Test error when object doesn't exist."""
        with pytest.raises(ValueError) as exc_info:
            uv_handler.unwrap(object_name="NonExistent")

        assert "not found" in str(exc_info.value)

    def test_unwrap_not_a_mesh(self, uv_handler, mock_mesh_object):
        """Test error when object is not a mesh."""
        mock_mesh_object.type = 'CAMERA'

        with pytest.raises(ValueError) as exc_info:
            uv_handler.unwrap(object_name="TestMesh")

        assert "not a mesh" in str(exc_info.value)

    def test_unwrap_invalid_method(self, uv_handler, mock_mesh_object):
        """Test error when invalid method is specified."""
        with pytest.raises(ValueError) as exc_info:
            uv_handler.unwrap(object_name="TestMesh", method="INVALID")

        assert "Unknown unwrap method" in str(exc_info.value)

    def test_unwrap_uses_active_object_when_no_name(self, uv_handler, mock_mesh_object):
        """Test that active object is used when object_name is None."""
        result = uv_handler.unwrap(object_name=None)

        assert "TestMesh" in result

    def test_unwrap_no_active_object(self, uv_handler, mock_no_active_object):
        """Test error when no active object and no object_name."""
        with pytest.raises(ValueError) as exc_info:
            uv_handler.unwrap(object_name=None)

        assert "No active object" in str(exc_info.value)


# =============================================================================
# uv_pack_islands Tests
# =============================================================================

class TestUVPackIslands:
    """Tests for uv_pack_islands functionality."""

    def test_pack_islands_default_params(self, uv_handler, mock_mesh_object):
        """Test pack islands with default parameters."""
        mock_mesh_object.mode = 'EDIT'

        result = uv_handler.pack_islands(object_name="TestMesh")

        bpy.ops.uv.select_all.assert_called_once_with(action='SELECT')
        bpy.ops.uv.pack_islands.assert_called_once_with(
            margin=0.02,
            rotate=True,
            scale=True
        )
        assert "TestMesh" in result
        assert "Packed" in result

    def test_pack_islands_custom_params(self, uv_handler, mock_mesh_object):
        """Test pack islands with custom parameters."""
        mock_mesh_object.mode = 'EDIT'

        result = uv_handler.pack_islands(
            object_name="TestMesh",
            margin=0.05,
            rotate=False,
            scale=False
        )

        bpy.ops.uv.pack_islands.assert_called_once_with(
            margin=0.05,
            rotate=False,
            scale=False
        )

    def test_pack_islands_object_not_found(self, uv_handler, mock_no_active_object):
        """Test error when object doesn't exist."""
        with pytest.raises(ValueError) as exc_info:
            uv_handler.pack_islands(object_name="NonExistent")

        assert "not found" in str(exc_info.value)

    def test_pack_islands_not_a_mesh(self, uv_handler, mock_mesh_object):
        """Test error when object is not a mesh."""
        mock_mesh_object.type = 'LIGHT'

        with pytest.raises(ValueError) as exc_info:
            uv_handler.pack_islands(object_name="TestMesh")

        assert "not a mesh" in str(exc_info.value)

    def test_pack_islands_enters_edit_mode(self, uv_handler, mock_mesh_object):
        """Test that pack_islands enters Edit mode if needed."""
        mock_mesh_object.mode = 'OBJECT'

        uv_handler.pack_islands(object_name="TestMesh")

        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')

    def test_pack_islands_no_active_object(self, uv_handler, mock_no_active_object):
        """Test error when no active object and no object_name."""
        with pytest.raises(ValueError) as exc_info:
            uv_handler.pack_islands(object_name=None)

        assert "No active object" in str(exc_info.value)


# =============================================================================
# uv_create_seam Tests
# =============================================================================

class TestUVCreateSeam:
    """Tests for uv_create_seam functionality."""

    def test_create_seam_mark(self, uv_handler, mock_mesh_object):
        """Test marking seams on selected edges."""
        mock_mesh_object.mode = 'EDIT'

        result = uv_handler.create_seam(object_name="TestMesh", action="mark")

        bpy.ops.mesh.mark_seam.assert_called_once_with(clear=False)
        assert "Marked seams" in result
        assert "TestMesh" in result

    def test_create_seam_clear(self, uv_handler, mock_mesh_object):
        """Test clearing seams from selected edges."""
        mock_mesh_object.mode = 'EDIT'

        result = uv_handler.create_seam(object_name="TestMesh", action="clear")

        bpy.ops.mesh.mark_seam.assert_called_once_with(clear=True)
        assert "Cleared seams" in result
        assert "TestMesh" in result

    def test_create_seam_invalid_action(self, uv_handler, mock_mesh_object):
        """Test error when invalid action is specified."""
        mock_mesh_object.mode = 'EDIT'

        with pytest.raises(ValueError) as exc_info:
            uv_handler.create_seam(object_name="TestMesh", action="invalid")

        assert "Unknown action" in str(exc_info.value)

    def test_create_seam_object_not_found(self, uv_handler, mock_no_active_object):
        """Test error when object doesn't exist."""
        with pytest.raises(ValueError) as exc_info:
            uv_handler.create_seam(object_name="NonExistent")

        assert "not found" in str(exc_info.value)

    def test_create_seam_not_a_mesh(self, uv_handler, mock_mesh_object):
        """Test error when object is not a mesh."""
        mock_mesh_object.type = 'EMPTY'

        with pytest.raises(ValueError) as exc_info:
            uv_handler.create_seam(object_name="TestMesh")

        assert "not a mesh" in str(exc_info.value)

    def test_create_seam_enters_edit_mode(self, uv_handler, mock_mesh_object):
        """Test that create_seam enters Edit mode if needed."""
        mock_mesh_object.mode = 'OBJECT'

        uv_handler.create_seam(object_name="TestMesh")

        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')

    def test_create_seam_uses_active_object(self, uv_handler, mock_mesh_object):
        """Test that active object is used when object_name is None."""
        mock_mesh_object.mode = 'EDIT'

        result = uv_handler.create_seam(object_name=None)

        assert "TestMesh" in result

    def test_create_seam_no_active_object(self, uv_handler, mock_no_active_object):
        """Test error when no active object and no object_name."""
        with pytest.raises(ValueError) as exc_info:
            uv_handler.create_seam(object_name=None)

        assert "No active object" in str(exc_info.value)
