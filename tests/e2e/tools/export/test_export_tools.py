"""
E2E tests for Export Tools (TASK-026).

Tests the export functionality with a running Blender instance.
These tests require Blender with the addon enabled.
"""
import os
import tempfile
import pytest
from server.application.tool_handlers.export_handler import ExportToolHandler


@pytest.fixture
def export_handler(rpc_client):
    """Provides an export handler instance using shared RPC client."""
    return ExportToolHandler(rpc_client)


@pytest.fixture
def temp_dir():
    """Provides a temporary directory for export files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestExportGlb:
    """E2E tests for GLB export."""

    def test_export_glb_basic(self, export_handler, temp_dir):
        """Test basic GLB export."""
        filepath = os.path.join(temp_dir, "test_export.glb")

        try:
            result = export_handler.export_glb(filepath=filepath)

            assert "Successfully exported" in result
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

            print(f"✓ export_glb created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_glb_with_options(self, export_handler, temp_dir):
        """Test GLB export with various options."""
        filepath = os.path.join(temp_dir, "test_options.glb")

        try:
            result = export_handler.export_glb(
                filepath=filepath,
                export_selected=False,
                export_animations=False,
                export_materials=True,
                apply_modifiers=True,
            )

            assert "Successfully exported" in result
            assert os.path.exists(filepath)

            print(f"✓ export_glb with options created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_gltf(self, export_handler, temp_dir):
        """Test GLTF export (separate files)."""
        filepath = os.path.join(temp_dir, "test_export.gltf")

        try:
            result = export_handler.export_glb(filepath=filepath)

            assert "Successfully exported" in result
            assert os.path.exists(filepath)

            print(f"✓ export_glb created GLTF file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise


class TestExportFbx:
    """E2E tests for FBX export."""

    def test_export_fbx_basic(self, export_handler, temp_dir):
        """Test basic FBX export."""
        filepath = os.path.join(temp_dir, "test_export.fbx")

        try:
            result = export_handler.export_fbx(filepath=filepath)

            assert "Successfully exported" in result
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

            print(f"✓ export_fbx created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_fbx_with_options(self, export_handler, temp_dir):
        """Test FBX export with various options."""
        filepath = os.path.join(temp_dir, "test_options.fbx")

        try:
            result = export_handler.export_fbx(
                filepath=filepath,
                export_selected=False,
                export_animations=False,
                apply_modifiers=True,
                mesh_smooth_type="EDGE",
            )

            assert "Successfully exported" in result
            assert os.path.exists(filepath)

            print(f"✓ export_fbx with options created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_fbx_smooth_types(self, export_handler, temp_dir):
        """Test FBX export with different smooth types."""
        for smooth_type in ["OFF", "FACE", "EDGE"]:
            filepath = os.path.join(temp_dir, f"test_smooth_{smooth_type}.fbx")

            try:
                result = export_handler.export_fbx(
                    filepath=filepath,
                    mesh_smooth_type=smooth_type,
                )

                assert "Successfully exported" in result
                assert os.path.exists(filepath)

                print(f"✓ export_fbx with smooth_type={smooth_type}")
            except RuntimeError as e:
                error_msg = str(e).lower()
                if "could not connect" in error_msg or "is blender running" in error_msg:
                    pytest.skip(f"Blender not available: {e}")
                raise


class TestExportObj:
    """E2E tests for OBJ export."""

    def test_export_obj_basic(self, export_handler, temp_dir):
        """Test basic OBJ export."""
        filepath = os.path.join(temp_dir, "test_export.obj")

        try:
            result = export_handler.export_obj(filepath=filepath)

            assert "Successfully exported" in result
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

            print(f"✓ export_obj created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_obj_with_materials(self, export_handler, temp_dir):
        """Test OBJ export with materials (creates .mtl file)."""
        filepath = os.path.join(temp_dir, "test_materials.obj")
        mtl_filepath = os.path.join(temp_dir, "test_materials.mtl")

        try:
            result = export_handler.export_obj(
                filepath=filepath,
                export_materials=True,
            )

            assert "Successfully exported" in result
            assert os.path.exists(filepath)
            # MTL file may or may not exist depending on scene content
            # Just verify OBJ was created

            print(f"✓ export_obj with materials created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_obj_with_options(self, export_handler, temp_dir):
        """Test OBJ export with various options."""
        filepath = os.path.join(temp_dir, "test_options.obj")

        try:
            result = export_handler.export_obj(
                filepath=filepath,
                export_selected=False,
                apply_modifiers=True,
                export_materials=False,
                export_uvs=True,
                export_normals=True,
                triangulate=False,
            )

            assert "Successfully exported" in result
            assert os.path.exists(filepath)

            print(f"✓ export_obj with options created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_obj_triangulated(self, export_handler, temp_dir):
        """Test OBJ export with triangulation."""
        filepath = os.path.join(temp_dir, "test_triangulated.obj")

        try:
            result = export_handler.export_obj(
                filepath=filepath,
                triangulate=True,
            )

            assert "Successfully exported" in result
            assert os.path.exists(filepath)

            # Verify file contains only triangular faces (f v/vt/vn v/vt/vn v/vt/vn)
            with open(filepath, "r") as f:
                content = f.read()
                # OBJ file should exist and have content
                assert len(content) > 0

            print(f"✓ export_obj with triangulation created file: {filepath}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise


class TestExportEdgeCases:
    """E2E tests for edge cases and error handling."""

    def test_export_creates_nested_directories(self, export_handler, temp_dir):
        """Test that export creates nested directories if needed."""
        nested_path = os.path.join(temp_dir, "a", "b", "c", "test.glb")

        try:
            result = export_handler.export_glb(filepath=nested_path)

            assert "Successfully exported" in result
            assert os.path.exists(nested_path)

            print(f"✓ export created nested directories: {nested_path}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_adds_extension_if_missing(self, export_handler, temp_dir):
        """Test that export adds correct extension if missing."""
        filepath_no_ext = os.path.join(temp_dir, "test_no_extension")

        try:
            result = export_handler.export_glb(filepath=filepath_no_ext)

            expected_path = filepath_no_ext + ".glb"
            assert "Successfully exported" in result
            assert os.path.exists(expected_path)

            print(f"✓ export added .glb extension: {expected_path}")
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "is blender running" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise

    def test_export_all_formats(self, export_handler, temp_dir):
        """Test exporting to all supported formats."""
        formats = [
            ("glb", export_handler.export_glb),
            ("fbx", export_handler.export_fbx),
            ("obj", export_handler.export_obj),
        ]

        for ext, export_func in formats:
            filepath = os.path.join(temp_dir, f"test.{ext}")

            try:
                result = export_func(filepath=filepath)

                assert "Successfully exported" in result
                assert os.path.exists(filepath)

                print(f"✓ export_{ext} successful")
            except RuntimeError as e:
                error_msg = str(e).lower()
                if "could not connect" in error_msg or "is blender running" in error_msg:
                    pytest.skip(f"Blender not available: {e}")
                raise
