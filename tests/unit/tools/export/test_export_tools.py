"""
Unit tests for export tools (TASK-026).

Tests the SystemHandler export methods:
- export_glb: Export to GLB/GLTF format
- export_fbx: Export to FBX format
- export_obj: Export to OBJ format
"""
import sys
import pytest
from unittest.mock import MagicMock, patch

from blender_addon.application.handlers.system import SystemHandler


# Get the mock_bpy from sys.modules (set by conftest.py)
mock_bpy = sys.modules['bpy']


class TestExportGlb:
    """Tests for export_glb method."""

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()
        self.handler = SystemHandler()

    def test_export_glb_basic(self):
        """Test basic GLB export with default parameters."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test.glb"
            )

        mock_bpy.ops.export_scene.gltf.assert_called_once()
        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]

        assert call_kwargs["filepath"] == "/tmp/test.glb"
        assert call_kwargs["export_format"] == "GLB"
        assert call_kwargs["use_selection"] is False
        assert call_kwargs["export_animations"] is True
        assert call_kwargs["export_materials"] == "EXPORT"
        assert call_kwargs["export_apply"] is True
        assert "Successfully exported" in result
        assert "/tmp/test.glb" in result

    def test_export_glb_gltf_extension(self):
        """Test GLTF export with .gltf extension."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test.gltf"
            )

        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]
        assert call_kwargs["export_format"] == "GLTF_SEPARATE"

    def test_export_glb_adds_extension(self):
        """Test that .glb extension is added if missing."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test"
            )

        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]
        assert call_kwargs["filepath"] == "/tmp/test.glb"
        assert call_kwargs["export_format"] == "GLB"

    def test_export_glb_selected_only(self):
        """Test GLB export with selected objects only."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test.glb",
                export_selected=True
            )

        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]
        assert call_kwargs["use_selection"] is True

    def test_export_glb_no_animations(self):
        """Test GLB export without animations."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test.glb",
                export_animations=False
            )

        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]
        assert call_kwargs["export_animations"] is False

    def test_export_glb_no_materials(self):
        """Test GLB export without materials."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test.glb",
                export_materials=False
            )

        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]
        assert call_kwargs["export_materials"] == "NONE"

    def test_export_glb_no_modifiers(self):
        """Test GLB export without applying modifiers."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test.glb",
                apply_modifiers=False
            )

        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]
        assert call_kwargs["export_apply"] is False

    def test_export_glb_creates_directory(self):
        """Test that directories are created if needed."""
        with patch("os.makedirs") as mock_makedirs:
            self.handler.export_glb(filepath="/tmp/subdir/test.glb")

        mock_makedirs.assert_called_once_with("/tmp/subdir", exist_ok=True)


class TestExportFbx:
    """Tests for export_fbx method."""

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()
        self.handler = SystemHandler()

    def test_export_fbx_basic(self):
        """Test basic FBX export with default parameters."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.fbx"
            )

        mock_bpy.ops.export_scene.fbx.assert_called_once()
        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]

        assert call_kwargs["filepath"] == "/tmp/test.fbx"
        assert call_kwargs["use_selection"] is False
        assert call_kwargs["bake_anim"] is True
        assert call_kwargs["use_mesh_modifiers"] is True
        assert call_kwargs["mesh_smooth_type"] == "FACE"
        assert call_kwargs["add_leaf_bones"] is False
        assert call_kwargs["primary_bone_axis"] == "Y"
        assert call_kwargs["secondary_bone_axis"] == "X"
        assert "Successfully exported" in result

    def test_export_fbx_adds_extension(self):
        """Test that .fbx extension is added if missing."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test"
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["filepath"] == "/tmp/test.fbx"

    def test_export_fbx_selected_only(self):
        """Test FBX export with selected objects only."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.fbx",
                export_selected=True
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["use_selection"] is True

    def test_export_fbx_no_animations(self):
        """Test FBX export without animations."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.fbx",
                export_animations=False
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["bake_anim"] is False

    def test_export_fbx_no_modifiers(self):
        """Test FBX export without applying modifiers."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.fbx",
                apply_modifiers=False
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["use_mesh_modifiers"] is False

    def test_export_fbx_smooth_type_edge(self):
        """Test FBX export with EDGE smoothing."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.fbx",
                mesh_smooth_type="EDGE"
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["mesh_smooth_type"] == "EDGE"

    def test_export_fbx_smooth_type_off(self):
        """Test FBX export with smoothing OFF."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.fbx",
                mesh_smooth_type="OFF"
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["mesh_smooth_type"] == "OFF"

    def test_export_fbx_invalid_smooth_type_defaults(self):
        """Test FBX export with invalid smooth type defaults to FACE."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.fbx",
                mesh_smooth_type="INVALID"
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["mesh_smooth_type"] == "FACE"

    def test_export_fbx_creates_directory(self):
        """Test that directories are created if needed."""
        with patch("os.makedirs") as mock_makedirs:
            self.handler.export_fbx(filepath="/tmp/subdir/test.fbx")

        mock_makedirs.assert_called_once_with("/tmp/subdir", exist_ok=True)


class TestExportObj:
    """Tests for export_obj method."""

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.ops.wm.obj_export.return_value = {'FINISHED'}
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()

        # Mock mesh objects in scene (required for OBJ export)
        mock_mesh_obj = MagicMock()
        mock_mesh_obj.type = 'MESH'
        mock_mesh_obj.name = 'Cube'
        mock_bpy.data.objects = [mock_mesh_obj]

        self.handler = SystemHandler()

    def test_export_obj_basic(self):
        """Test basic OBJ export with default parameters."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj"
            )

        mock_bpy.ops.wm.obj_export.assert_called_once()
        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]

        assert call_kwargs["filepath"] == "/tmp/test.obj"
        assert call_kwargs["export_selected_objects"] is False
        assert call_kwargs["apply_modifiers"] is True
        assert call_kwargs["export_materials"] is True
        assert call_kwargs["export_uv"] is True
        assert call_kwargs["export_normals"] is True
        assert call_kwargs["export_triangulated_mesh"] is False
        assert "Successfully exported" in result

    def test_export_obj_adds_extension(self):
        """Test that .obj extension is added if missing."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test"
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["filepath"] == "/tmp/test.obj"

    def test_export_obj_selected_only(self):
        """Test OBJ export with selected objects only."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj",
                export_selected=True
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["export_selected_objects"] is True

    def test_export_obj_no_modifiers(self):
        """Test OBJ export without applying modifiers."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj",
                apply_modifiers=False
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["apply_modifiers"] is False

    def test_export_obj_no_materials(self):
        """Test OBJ export without materials."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj",
                export_materials=False
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["export_materials"] is False

    def test_export_obj_no_uvs(self):
        """Test OBJ export without UVs."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj",
                export_uvs=False
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["export_uv"] is False

    def test_export_obj_no_normals(self):
        """Test OBJ export without normals."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj",
                export_normals=False
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["export_normals"] is False

    def test_export_obj_triangulate(self):
        """Test OBJ export with triangulation."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj",
                triangulate=True
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["export_triangulated_mesh"] is True

    def test_export_obj_creates_directory(self):
        """Test that directories are created if needed."""
        with patch("os.makedirs") as mock_makedirs, \
             patch("os.access", return_value=True), \
             patch("os.path.exists", return_value=True), \
             patch("os.listdir", return_value=["test.obj"]):
            self.handler.export_obj(filepath="/tmp/subdir/test.obj")

        mock_makedirs.assert_called_once_with("/tmp/subdir", exist_ok=True)

    def test_export_obj_all_options_disabled(self):
        """Test OBJ export with all optional features disabled."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.obj",
                export_selected=True,
                apply_modifiers=False,
                export_materials=False,
                export_uvs=False,
                export_normals=False,
                triangulate=True
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["export_selected_objects"] is True
        assert call_kwargs["apply_modifiers"] is False
        assert call_kwargs["export_materials"] is False
        assert call_kwargs["export_uv"] is False
        assert call_kwargs["export_normals"] is False
        assert call_kwargs["export_triangulated_mesh"] is True


class TestExportEdgeCases:
    """Tests for edge cases and special scenarios."""

    def setup_method(self):
        """Reset mock and reconfigure before each test."""
        mock_bpy.reset_mock()
        mock_bpy.ops = MagicMock()
        mock_bpy.ops.wm.obj_export.return_value = {'FINISHED'}
        mock_bpy.data = MagicMock()
        mock_bpy.context = MagicMock()

        # Mock mesh objects in scene (required for OBJ export)
        mock_mesh_obj = MagicMock()
        mock_mesh_obj.type = 'MESH'
        mock_mesh_obj.name = 'Cube'
        mock_bpy.data.objects = [mock_mesh_obj]

        self.handler = SystemHandler()

    def test_export_glb_uppercase_extension(self):
        """Test GLB export with uppercase extension."""
        with patch("os.makedirs"):
            result = self.handler.export_glb(
                filepath="/tmp/test.GLB"
            )

        call_kwargs = mock_bpy.ops.export_scene.gltf.call_args[1]
        assert call_kwargs["export_format"] == "GLB"

    def test_export_fbx_uppercase_extension(self):
        """Test FBX export with uppercase extension."""
        with patch("os.makedirs"):
            result = self.handler.export_fbx(
                filepath="/tmp/test.FBX"
            )

        call_kwargs = mock_bpy.ops.export_scene.fbx.call_args[1]
        assert call_kwargs["filepath"] == "/tmp/test.FBX"

    def test_export_obj_uppercase_extension(self):
        """Test OBJ export with uppercase extension."""
        with patch("os.makedirs"), patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="/tmp/test.OBJ"
            )

        call_kwargs = mock_bpy.ops.wm.obj_export.call_args[1]
        assert call_kwargs["filepath"] == "/tmp/test.OBJ"

    def test_export_glb_empty_directory(self):
        """Test GLB export to current directory (no dir path)."""
        with patch("os.makedirs") as mock_makedirs:
            result = self.handler.export_glb(
                filepath="test.glb"
            )

        # makedirs should not be called for empty dir path
        mock_makedirs.assert_not_called()

    def test_export_fbx_empty_directory(self):
        """Test FBX export to current directory (no dir path)."""
        with patch("os.makedirs") as mock_makedirs:
            result = self.handler.export_fbx(
                filepath="test.fbx"
            )

        mock_makedirs.assert_not_called()

    def test_export_obj_empty_directory(self):
        """Test OBJ export to current directory (no dir path)."""
        with patch("os.makedirs") as mock_makedirs, patch("os.access", return_value=True), patch("os.path.exists", return_value=True):
            result = self.handler.export_obj(
                filepath="test.obj"
            )

        mock_makedirs.assert_not_called()
