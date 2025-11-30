"""Unit tests for Import Handler (TASK-035).

Tests SystemHandler import methods after consolidation.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys

from blender_addon.application.handlers.system import SystemHandler


# Get the mock_bpy from sys.modules (set by conftest.py)
mock_bpy = sys.modules['bpy']


class TestImportOBJ:
    """Tests for import_obj method."""

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()
        mock_bpy.data.objects.keys.return_value = []
        self.handler = SystemHandler()

    @patch('os.path.exists')
    def test_import_obj_basic(self, mock_exists):
        """Test basic OBJ import."""
        mock_exists.return_value = True
        mock_bpy.data.objects.keys.side_effect = [
            [],  # before import
            ['ImportedMesh']  # after import
        ]

        result = self.handler.import_obj(filepath="/path/to/model.obj")

        mock_bpy.ops.wm.obj_import.assert_called_once()
        assert "Successfully imported" in result
        assert "ImportedMesh" in result

    @patch('os.path.exists')
    def test_import_obj_file_not_found(self, mock_exists):
        """Test OBJ import with missing file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as excinfo:
            self.handler.import_obj(filepath="/missing/model.obj")

        assert "OBJ file not found" in str(excinfo.value)

    @patch('os.path.exists')
    def test_import_obj_with_scale(self, mock_exists):
        """Test OBJ import with custom scale."""
        mock_exists.return_value = True
        mock_bpy.data.objects.keys.side_effect = [[], ['Mesh']]

        result = self.handler.import_obj(
            filepath="/path/to/model.obj",
            global_scale=2.0,
            use_split_objects=False
        )

        call_kwargs = mock_bpy.ops.wm.obj_import.call_args[1]
        assert call_kwargs['global_scale'] == 2.0
        assert call_kwargs['use_split_objects'] is False


class TestImportFBX:
    """Tests for import_fbx method."""

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()
        mock_bpy.data.objects.keys.return_value = []
        self.handler = SystemHandler()

    @patch('os.path.exists')
    def test_import_fbx_basic(self, mock_exists):
        """Test basic FBX import."""
        mock_exists.return_value = True
        mock_bpy.data.objects.keys.side_effect = [
            [],
            ['Character', 'Armature']
        ]

        result = self.handler.import_fbx(filepath="/path/to/character.fbx")

        mock_bpy.ops.import_scene.fbx.assert_called_once()
        assert "Successfully imported" in result
        assert "Character" in result

    @patch('os.path.exists')
    def test_import_fbx_file_not_found(self, mock_exists):
        """Test FBX import with missing file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as excinfo:
            self.handler.import_fbx(filepath="/missing/model.fbx")

        assert "FBX file not found" in str(excinfo.value)

    @patch('os.path.exists')
    def test_import_fbx_with_options(self, mock_exists):
        """Test FBX import with custom options."""
        mock_exists.return_value = True
        mock_bpy.data.objects.keys.side_effect = [[], ['Model']]

        result = self.handler.import_fbx(
            filepath="/path/to/model.fbx",
            use_custom_normals=False,
            ignore_leaf_bones=True,
            global_scale=0.01
        )

        call_kwargs = mock_bpy.ops.import_scene.fbx.call_args[1]
        assert call_kwargs['use_custom_normals'] is False
        assert call_kwargs['ignore_leaf_bones'] is True
        assert call_kwargs['global_scale'] == 0.01


class TestImportGLB:
    """Tests for import_glb method."""

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()
        mock_bpy.data.objects.keys.return_value = []
        self.handler = SystemHandler()

    @patch('os.path.exists')
    def test_import_glb_basic(self, mock_exists):
        """Test basic GLB import."""
        mock_exists.return_value = True
        mock_bpy.data.objects.keys.side_effect = [
            [],
            ['SceneRoot', 'Mesh']
        ]

        result = self.handler.import_glb(filepath="/path/to/model.glb")

        mock_bpy.ops.import_scene.gltf.assert_called_once()
        assert "Successfully imported" in result
        assert "Mesh" in result

    @patch('os.path.exists')
    def test_import_glb_file_not_found(self, mock_exists):
        """Test GLB import with missing file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as excinfo:
            self.handler.import_glb(filepath="/missing/model.glb")

        assert "GLB/GLTF file not found" in str(excinfo.value)

    @patch('os.path.exists')
    def test_import_glb_with_options(self, mock_exists):
        """Test GLB import with custom options."""
        mock_exists.return_value = True
        mock_bpy.data.objects.keys.side_effect = [[], ['Model']]

        result = self.handler.import_glb(
            filepath="/path/to/model.gltf",
            import_pack_images=False,
            merge_vertices=True,
            import_shading="SMOOTH"
        )

        call_kwargs = mock_bpy.ops.import_scene.gltf.call_args[1]
        assert call_kwargs['import_pack_images'] is False
        assert call_kwargs['merge_vertices'] is True
        assert call_kwargs['import_shading'] == "SMOOTH"


class TestImportImageAsPlane:
    """Tests for import_image_as_plane method.

    The implementation creates a plane manually without using the addon:
    1. Loads image with bpy.data.images.load()
    2. Creates a plane with bpy.ops.mesh.primitive_plane_add()
    3. Creates material with shader nodes
    """

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()

        # Mock image loading
        mock_image = MagicMock()
        mock_image.size = (1920, 1080)  # Sample image dimensions
        mock_bpy.data.images.load.return_value = mock_image

        # Mock plane object created by primitive_plane_add
        self.mock_plane = MagicMock()
        self.mock_plane.name = 'TestPlane'
        self.mock_plane.data.materials = []
        mock_bpy.context.active_object = self.mock_plane

        # Mock material creation
        mock_material = MagicMock()
        mock_material.use_nodes = True
        mock_material.node_tree = MagicMock()
        mock_material.node_tree.nodes = MagicMock()
        mock_material.node_tree.links = MagicMock()
        mock_bpy.data.materials.new.return_value = mock_material

        self.handler = SystemHandler()

    @patch('os.path.exists')
    def test_import_image_basic(self, mock_exists):
        """Test basic image as plane import."""
        mock_exists.return_value = True

        result = self.handler.import_image_as_plane(filepath="/path/to/reference.png")

        # Verify image was loaded
        mock_bpy.data.images.load.assert_called_once_with("/path/to/reference.png")
        # Verify plane was created
        mock_bpy.ops.mesh.primitive_plane_add.assert_called_once()
        # Verify material was created
        mock_bpy.data.materials.new.assert_called_once()
        assert "Successfully imported" in result

    @patch('os.path.exists')
    def test_import_image_file_not_found(self, mock_exists):
        """Test image import with missing file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as excinfo:
            self.handler.import_image_as_plane(filepath="/missing/image.png")

        assert "Image file not found" in str(excinfo.value)

    @patch('os.path.exists')
    def test_import_image_with_custom_name(self, mock_exists):
        """Test image import with custom plane name."""
        mock_exists.return_value = True

        result = self.handler.import_image_as_plane(
            filepath="/path/to/image.png",
            name="RefImage",
            location=[1.0, 2.0, 0.0],
            size=2.0
        )

        # Verify plane was created
        mock_bpy.ops.mesh.primitive_plane_add.assert_called_once()
        # Verify plane name was set
        assert self.mock_plane.name == "RefImage"
        # Verify location was set
        assert self.mock_plane.location == [1.0, 2.0, 0.0]

    @patch('os.path.exists')
    def test_import_image_creates_material(self, mock_exists):
        """Test that import creates a material with shader nodes."""
        mock_exists.return_value = True

        result = self.handler.import_image_as_plane(filepath="/path/to/image.png")

        # Verify material was created
        mock_bpy.data.materials.new.assert_called_once()
        assert "Successfully imported" in result
