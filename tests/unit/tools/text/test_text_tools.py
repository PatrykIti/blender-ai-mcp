"""
Tests for TASK-034 (Text & Annotations) text tools.
Pure pytest style - uses conftest.py fixtures.
"""
import pytest
from unittest.mock import MagicMock, patch

import bpy

from blender_addon.application.handlers.text import TextHandler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def text_handler():
    """Provides a fresh TextHandler instance."""
    return TextHandler()


@pytest.fixture
def mock_text_object():
    """Sets up mock text object."""
    mock_obj = MagicMock()
    mock_obj.name = 'Text'
    mock_obj.type = 'FONT'
    mock_obj.data = MagicMock()
    mock_obj.data.body = 'Hello'
    mock_obj.data.size = 1.0
    mock_obj.data.extrude = 0.0
    mock_obj.data.bevel_depth = 0.0
    mock_obj.data.bevel_resolution = 0
    mock_obj.data.align_x = 'LEFT'
    mock_obj.data.align_y = 'BOTTOM_BASELINE'
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
# TASK-034-1: text_create tests
# =============================================================================

class TestTextCreate:
    """Tests for text_create tool."""

    def test_create_default_text(self, text_handler, mock_text_object):
        """Should create text at default location with default content."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.create()

        bpy.ops.object.text_add.assert_called_with(location=(0, 0, 0))
        assert "Created text object" in result
        assert "Text" in result

    def test_create_text_with_content(self, text_handler, mock_text_object):
        """Should create text with specified content."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.create(text="Hello World", name="MyText")

        assert mock_text_object.data.body == "Hello World"
        assert "Hello World" in result

    def test_create_text_with_location(self, text_handler, mock_text_object):
        """Should create text at specified location."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.create(location=[1, 2, 3])

        bpy.ops.object.text_add.assert_called_with(location=(1, 2, 3))
        assert "[1, 2, 3]" in result

    def test_create_text_with_extrude(self, text_handler, mock_text_object):
        """Should create text with extrusion."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.create(text="3D", extrude=0.5)

        assert mock_text_object.data.extrude == 0.5
        assert "extrude=0.5" in result

    def test_create_text_with_bevel(self, text_handler, mock_text_object):
        """Should create text with bevel."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.create(text="Beveled", bevel_depth=0.02, bevel_resolution=4)

        assert mock_text_object.data.bevel_depth == 0.02
        assert mock_text_object.data.bevel_resolution == 4
        assert "bevel_depth=0.02" in result

    def test_create_text_with_alignment(self, text_handler, mock_text_object):
        """Should create text with specified alignment."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.create(text="Centered", align_x="CENTER", align_y="CENTER")

        assert mock_text_object.data.align_x == "CENTER"
        assert mock_text_object.data.align_y == "MIDDLE"

    def test_create_text_invalid_align_x_raises(self, text_handler, mock_text_object):
        """Should raise ValueError for invalid align_x."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        with pytest.raises(ValueError, match="Invalid align_x"):
            text_handler.create(align_x="INVALID")

    def test_create_text_invalid_align_y_raises(self, text_handler, mock_text_object):
        """Should raise ValueError for invalid align_y."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        with pytest.raises(ValueError, match="Invalid align_y"):
            text_handler.create(align_y="INVALID")

    def test_create_text_case_insensitive_alignment(self, text_handler, mock_text_object):
        """Should handle case-insensitive alignment values."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.create(align_x="center", align_y="middle")

        assert mock_text_object.data.align_x == "CENTER"
        assert mock_text_object.data.align_y == "MIDDLE"

    def test_create_text_font_not_found_raises(self, text_handler, mock_text_object):
        """Should raise ValueError when font file not found."""
        bpy.ops.object.text_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.mode = 'OBJECT'

        with pytest.raises(ValueError, match="Font file not found"):
            text_handler.create(font="/nonexistent/font.ttf")


# =============================================================================
# TASK-034-2: text_edit tests
# =============================================================================

class TestTextEdit:
    """Tests for text_edit tool."""

    def test_edit_text_content(self, text_handler, mock_text_object):
        """Should edit text content."""
        bpy.data.objects = {'Text': mock_text_object}

        result = text_handler.edit(object_name='Text', text='New Content')

        assert mock_text_object.data.body == 'New Content'
        assert 'text="New Content"' in result

    def test_edit_text_size(self, text_handler, mock_text_object):
        """Should edit text size."""
        bpy.data.objects = {'Text': mock_text_object}

        result = text_handler.edit(object_name='Text', size=2.5)

        assert mock_text_object.data.size == 2.5
        assert 'size=2.5' in result

    def test_edit_text_extrude(self, text_handler, mock_text_object):
        """Should edit text extrude."""
        bpy.data.objects = {'Text': mock_text_object}

        result = text_handler.edit(object_name='Text', extrude=0.3)

        assert mock_text_object.data.extrude == 0.3
        assert 'extrude=0.3' in result

    def test_edit_text_multiple_properties(self, text_handler, mock_text_object):
        """Should edit multiple text properties at once."""
        bpy.data.objects = {'Text': mock_text_object}

        result = text_handler.edit(
            object_name='Text',
            text='Updated',
            size=1.5,
            extrude=0.2,
            align_x='CENTER'
        )

        assert mock_text_object.data.body == 'Updated'
        assert mock_text_object.data.size == 1.5
        assert mock_text_object.data.extrude == 0.2
        assert mock_text_object.data.align_x == 'CENTER'
        assert 'Modified text object' in result

    def test_edit_text_no_changes(self, text_handler, mock_text_object):
        """Should report no changes when no parameters provided."""
        bpy.data.objects = {'Text': mock_text_object}

        result = text_handler.edit(object_name='Text')

        assert 'unchanged' in result

    def test_edit_text_not_found_raises(self, text_handler):
        """Should raise ValueError when object not found."""
        bpy.data.objects = {}

        with pytest.raises(ValueError, match="not found"):
            text_handler.edit(object_name='NonExistent')

    def test_edit_non_text_object_raises(self, text_handler, mock_mesh_object):
        """Should raise ValueError when object is not a text object."""
        bpy.data.objects = {'Cube': mock_mesh_object}

        with pytest.raises(ValueError, match="not a text object"):
            text_handler.edit(object_name='Cube')

    def test_edit_text_invalid_align_x_raises(self, text_handler, mock_text_object):
        """Should raise ValueError for invalid align_x."""
        bpy.data.objects = {'Text': mock_text_object}

        with pytest.raises(ValueError, match="Invalid align_x"):
            text_handler.edit(object_name='Text', align_x='INVALID')


# =============================================================================
# TASK-034-3: text_to_mesh tests
# =============================================================================

class TestTextToMesh:
    """Tests for text_to_mesh tool."""

    def test_convert_text_to_mesh(self, text_handler, mock_text_object):
        """Should convert text to mesh."""
        bpy.data.objects = {'Text': mock_text_object}
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.convert = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.view_layer = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.to_mesh('Text')

        bpy.ops.object.convert.assert_called_with(target='MESH')
        assert "Converted text" in result
        assert "to mesh" in result

    def test_convert_text_keep_original(self, text_handler, mock_text_object):
        """Should keep original text when keep_original=True."""
        bpy.data.objects = {'Text': mock_text_object}
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.duplicate = MagicMock()
        bpy.ops.object.convert = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.context.view_layer = MagicMock()
        bpy.context.mode = 'OBJECT'

        result = text_handler.to_mesh('Text', keep_original=True)

        bpy.ops.object.duplicate.assert_called_once()
        bpy.ops.object.convert.assert_called_with(target='MESH')
        assert "original preserved" in result

    def test_convert_text_not_found_raises(self, text_handler):
        """Should raise ValueError when object not found."""
        bpy.data.objects = {}

        with pytest.raises(ValueError, match="not found"):
            text_handler.to_mesh('NonExistent')

    def test_convert_non_text_raises(self, text_handler, mock_mesh_object):
        """Should raise ValueError when object is not text."""
        bpy.data.objects = {'Cube': mock_mesh_object}

        with pytest.raises(ValueError, match="not a text object"):
            text_handler.to_mesh('Cube')
