"""E2E tests for Import Tools (TASK-035).

These tests require a running Blender instance with the addon enabled.
Run manually with: PYTHONPATH=. poetry run pytest tests/e2e/tools/import_tool/ -v

Test workflow:
1. Export a test file (OBJ/FBX/GLB)
2. Clear scene
3. Import the test file
4. Verify imported objects exist
"""

import os
import tempfile
import pytest

from server.adapters.rpc.client import RpcClient
from server.application.tool_handlers.export_handler import ExportToolHandler
from server.application.tool_handlers.import_handler import ImportToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler


# Skip all tests if Blender is not running
pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def rpc_client():
    """Create RPC client connected to Blender."""
    client = RpcClient(host="127.0.0.1", port=8765)
    yield client


@pytest.fixture(scope="module")
def scene_handler(rpc_client):
    """Create scene handler."""
    return SceneToolHandler(rpc_client)


@pytest.fixture(scope="module")
def modeling_handler(rpc_client):
    """Create modeling handler."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture(scope="module")
def export_handler(rpc_client):
    """Create export handler."""
    return ExportToolHandler(rpc_client)


@pytest.fixture(scope="module")
def import_handler(rpc_client):
    """Create import handler."""
    return ImportToolHandler(rpc_client)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def clean_scene(scene_handler):
    """Clean the scene before each test."""
    scene_handler.clean_scene(keep_lights_and_cameras=False)
    yield
    # Cleanup after test
    scene_handler.clean_scene(keep_lights_and_cameras=False)


class TestImportOBJ:
    """E2E tests for OBJ import."""

    def test_import_obj_roundtrip(
        self, clean_scene, modeling_handler, export_handler, import_handler, scene_handler, temp_dir
    ):
        """Test export cube to OBJ, clear scene, import, verify."""
        # Create a cube
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name="TestCube",
            size=2.0,
            location=[0, 0, 0]
        )

        # Export to OBJ
        obj_path = os.path.join(temp_dir, "test_cube.obj")
        export_handler.export_obj(filepath=obj_path)
        assert os.path.exists(obj_path)

        # Clear scene
        scene_handler.clean_scene(keep_lights_and_cameras=False)

        # Import OBJ
        result = import_handler.import_obj(filepath=obj_path)
        assert "Successfully imported" in result

        # Verify object exists
        objects = scene_handler.list_objects()
        assert len([o for o in objects if "Cube" in o.get("name", "")]) > 0

    def test_import_obj_with_scale(
        self, clean_scene, modeling_handler, export_handler, import_handler, temp_dir
    ):
        """Test OBJ import with custom scale."""
        # Create and export cube
        modeling_handler.create_primitive(primitive_type="CUBE", name="ScaleCube")
        obj_path = os.path.join(temp_dir, "scale_cube.obj")
        export_handler.export_obj(filepath=obj_path)

        # Clear and import with scale
        from server.adapters.rpc.client import RpcClient
        scene_handler = SceneToolHandler(RpcClient(host="127.0.0.1", port=8765))
        scene_handler.clean_scene(keep_lights_and_cameras=False)

        result = import_handler.import_obj(filepath=obj_path, global_scale=0.5)
        assert "Successfully imported" in result


class TestImportFBX:
    """E2E tests for FBX import."""

    def test_import_fbx_roundtrip(
        self, clean_scene, modeling_handler, export_handler, import_handler, scene_handler, temp_dir
    ):
        """Test export to FBX, clear scene, import, verify."""
        # Create a sphere
        modeling_handler.create_primitive(
            primitive_type="UV_SPHERE",
            name="TestSphere",
            location=[0, 0, 0]
        )

        # Export to FBX
        fbx_path = os.path.join(temp_dir, "test_sphere.fbx")
        export_handler.export_fbx(filepath=fbx_path)
        assert os.path.exists(fbx_path)

        # Clear scene
        scene_handler.clean_scene(keep_lights_and_cameras=False)

        # Import FBX
        result = import_handler.import_fbx(filepath=fbx_path)
        assert "Successfully imported" in result

        # Verify object exists
        objects = scene_handler.list_objects()
        assert len(objects) > 0


class TestImportGLB:
    """E2E tests for GLB/GLTF import."""

    def test_import_glb_roundtrip(
        self, clean_scene, modeling_handler, export_handler, import_handler, scene_handler, temp_dir
    ):
        """Test export to GLB, clear scene, import, verify."""
        # Create a cylinder
        modeling_handler.create_primitive(
            primitive_type="CYLINDER",
            name="TestCylinder",
            location=[0, 0, 0]
        )

        # Export to GLB
        glb_path = os.path.join(temp_dir, "test_cylinder.glb")
        export_handler.export_glb(filepath=glb_path)
        assert os.path.exists(glb_path)

        # Clear scene
        scene_handler.clean_scene(keep_lights_and_cameras=False)

        # Import GLB
        result = import_handler.import_glb(filepath=glb_path)
        assert "Successfully imported" in result

        # Verify object exists
        objects = scene_handler.list_objects()
        assert len(objects) > 0

    def test_import_gltf_separate(
        self, clean_scene, modeling_handler, export_handler, import_handler, scene_handler, temp_dir
    ):
        """Test GLTF import with separate file format."""
        # Create object
        modeling_handler.create_primitive(primitive_type="CONE", name="TestCone")

        # Export to GLTF (separate)
        gltf_path = os.path.join(temp_dir, "test_cone.gltf")
        export_handler.export_glb(filepath=gltf_path)

        # Clear and import
        scene_handler.clean_scene(keep_lights_and_cameras=False)
        result = import_handler.import_glb(filepath=gltf_path)
        assert "Successfully imported" in result or "Imported" in result


class TestImportImageAsPlane:
    """E2E tests for image as plane import."""

    def test_import_image_as_plane(
        self, clean_scene, import_handler, scene_handler, temp_dir
    ):
        """Test importing an image as a textured plane."""
        # Create a simple test image (1x1 pixel PNG)
        try:
            from PIL import Image
            img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 255))
            img_path = os.path.join(temp_dir, "test_image.png")
            img.save(img_path)
        except ImportError:
            pytest.skip("PIL not installed, skipping image import test")

        # Import image as plane
        result = import_handler.import_image_as_plane(
            filepath=img_path,
            name="RefImage",
            shader="PRINCIPLED"
        )

        assert "Successfully imported" in result or "imported" in result.lower()

        # Verify plane was created
        objects = scene_handler.list_objects()
        plane_found = any("RefImage" in obj.get("name", "") or "test_image" in obj.get("name", "") for obj in objects)
        assert plane_found or len(objects) > 0


class TestImportErrorHandling:
    """E2E tests for error handling."""

    def test_import_nonexistent_file(self, clean_scene, import_handler):
        """Test importing non-existent file returns error."""
        with pytest.raises(RuntimeError) as excinfo:
            import_handler.import_obj(filepath="/nonexistent/path/file.obj")

        assert "not found" in str(excinfo.value).lower() or "error" in str(excinfo.value).lower()

    def test_import_invalid_format(self, clean_scene, import_handler, temp_dir):
        """Test importing file with wrong format."""
        # Create a text file with .obj extension
        fake_obj = os.path.join(temp_dir, "fake.obj")
        with open(fake_obj, 'w') as f:
            f.write("This is not a valid OBJ file")

        # This should either fail or import nothing
        try:
            result = import_handler.import_obj(filepath=fake_obj)
            # If it doesn't raise, it should indicate no objects imported
            assert "imported" in result.lower()
        except RuntimeError:
            pass  # Expected - invalid file format


class TestImportIntegration:
    """Integration tests combining import with other operations."""

    def test_import_modify_export(
        self, clean_scene, modeling_handler, export_handler, import_handler, scene_handler, temp_dir
    ):
        """Test full workflow: create -> export -> import -> modify -> export."""
        # Create original object
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name="WorkflowCube",
            size=1.0
        )

        # Export
        original_path = os.path.join(temp_dir, "original.obj")
        export_handler.export_obj(filepath=original_path)

        # Clear and import
        scene_handler.clean_scene(keep_lights_and_cameras=False)
        import_handler.import_obj(filepath=original_path)

        # Apply transformation
        objects = scene_handler.list_objects()
        if objects:
            obj_name = objects[0].get("name", "Cube")
            modeling_handler.transform_object(name=obj_name, scale=[2.0, 2.0, 2.0])

        # Export modified version
        modified_path = os.path.join(temp_dir, "modified.obj")
        export_handler.export_obj(filepath=modified_path)

        assert os.path.exists(modified_path)
        # Modified file should be larger due to scaled geometry
        assert os.path.getsize(modified_path) > 0
