"""
Tests for Material Tools (TASK-014-8, 014-9, TASK-023)
"""
import pytest
from server.application.tool_handlers.material_handler import MaterialToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def material_handler(rpc_client):
    """Provides a material handler instance using shared RPC client."""
    return MaterialToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def test_material_list(material_handler):
    """Test listing materials."""
    try:
        result = material_handler.list_materials(include_unassigned=True)
        assert isinstance(result, list)

        if result:
            # Check structure of first material
            first_mat = result[0]
            assert "name" in first_mat
            assert "use_nodes" in first_mat
            assert "assigned_object_count" in first_mat

        print(f"✓ material_list returned {len(result)} materials")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_material_list_exclude_unassigned(material_handler):
    """Test listing materials excluding unassigned ones."""
    try:
        result = material_handler.list_materials(include_unassigned=False)
        assert isinstance(result, list)

        # All materials should have assigned_object_count > 0
        for mat in result:
            assert mat["assigned_object_count"] > 0, f"Material {mat['name']} is unassigned"

        print(f"✓ material_list (assigned only): {len(result)} materials")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_material_list_by_object(material_handler, modeling_handler, scene_handler):
    """Test listing material slots by object."""
    obj_name = "E2E_MatListTest"
    try:
        # Clean up if exists
        try:
            scene_handler.delete_object(obj_name)
        except RuntimeError:
            pass

        # Create test object
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=obj_name,
            location=[0, 0, 0]
        )

        # List material slots
        result = material_handler.list_by_object(
            object_name=obj_name,
            include_indices=False
        )

        assert isinstance(result, dict)
        assert "object_name" in result
        assert "slot_count" in result
        assert "slots" in result
        assert isinstance(result["slots"], list)

        print(f"✓ material_list_by_object: '{result['object_name']}' has {result['slot_count']} slots")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        # Cleanup
        try:
            scene_handler.delete_object(obj_name)
        except RuntimeError:
            pass


def test_material_list_by_object_invalid(material_handler):
    """Test listing material slots with invalid object name."""
    try:
        material_handler.list_by_object(
            object_name="NonExistentObject12345",
            include_indices=False
        )
        # If we get here without exception, test should fail
        assert False, "Expected RuntimeError for invalid object name"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ material_list_by_object properly handles invalid object name")
        else:
            raise  # Re-raise unexpected errors


# TASK-023-1: material_create
def test_material_create_basic(material_handler):
    """Test creating a basic material."""
    try:
        result = material_handler.create_material(name="E2E_TestMaterial")
        assert "Created material" in result
        print(f"✓ material_create: {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_material_create_with_params(material_handler):
    """Test creating a material with custom parameters."""
    try:
        result = material_handler.create_material(
            name="E2E_ColorMaterial",
            base_color=[1.0, 0.0, 0.0, 1.0],
            metallic=0.8,
            roughness=0.2,
        )
        assert "Created material" in result
        print(f"✓ material_create (with params): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_material_create_with_emission(material_handler):
    """Test creating a material with emission."""
    try:
        result = material_handler.create_material(
            name="E2E_EmissiveMaterial",
            emission_color=[0.0, 1.0, 0.0],
            emission_strength=5.0,
        )
        assert "Created material" in result
        print(f"✓ material_create (emissive): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_material_create_transparent(material_handler):
    """Test creating a transparent material."""
    try:
        result = material_handler.create_material(
            name="E2E_TransparentMaterial",
            alpha=0.5,
        )
        assert "Created material" in result
        print(f"✓ material_create (transparent): {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# TASK-023-2: material_assign
def test_material_assign_to_object(material_handler, modeling_handler, scene_handler):
    """Test assigning material to an object."""
    obj_name = "E2E_MatAssignTest"
    mat_name = "E2E_AssignMaterial"
    try:
        # Clean up if exists
        try:
            scene_handler.delete_object(obj_name)
        except RuntimeError:
            pass

        # Create test object
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=obj_name,
            location=[0, 0, 0]
        )

        # Create a test material
        material_handler.create_material(name=mat_name)

        # Assign material to object
        result = material_handler.assign_material(
            material_name=mat_name,
            object_name=obj_name
        )

        assert "Assigned" in result
        print(f"✓ material_assign: {result}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
    finally:
        # Cleanup
        try:
            scene_handler.delete_object(obj_name)
        except RuntimeError:
            pass


def test_material_assign_invalid_material(material_handler):
    """Test assigning non-existent material."""
    try:
        material_handler.assign_material(
            material_name="NonExistentMaterial12345",
            object_name="Cube"
        )
        assert False, "Expected RuntimeError for invalid material"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ material_assign properly handles invalid material name")
        else:
            raise


# TASK-023-3: material_set_params
def test_material_set_params(material_handler):
    """Test modifying material parameters."""
    try:
        # First, create a test material
        material_handler.create_material(name="E2E_ModifyMaterial")

        # Modify parameters
        result = material_handler.set_material_params(
            material_name="E2E_ModifyMaterial",
            roughness=0.9,
            metallic=0.1,
        )
        assert "Updated" in result
        assert "roughness" in result
        assert "metallic" in result
        print(f"✓ material_set_params: {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_material_set_params_invalid_material(material_handler):
    """Test modifying non-existent material."""
    try:
        material_handler.set_material_params(
            material_name="NonExistentMaterial12345",
            roughness=0.5
        )
        assert False, "Expected RuntimeError for invalid material"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ material_set_params properly handles invalid material name")
        else:
            raise


# TASK-023-4: material_set_texture
def test_material_set_texture_invalid_material(material_handler):
    """Test setting texture on non-existent material."""
    try:
        material_handler.set_material_texture(
            material_name="NonExistentMaterial12345",
            texture_path="/tmp/test.png"
        )
        assert False, "Expected RuntimeError for invalid material"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ material_set_texture properly handles invalid material name")
        else:
            raise


def test_material_set_texture_invalid_path(material_handler):
    """Test setting texture with invalid file path."""
    try:
        # First, create a test material
        material_handler.create_material(name="E2E_TextureMaterial")

        # Try to set texture with non-existent file
        material_handler.set_material_texture(
            material_name="E2E_TextureMaterial",
            texture_path="/nonexistent/path/to/texture.png"
        )
        assert False, "Expected RuntimeError for invalid texture path"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "failed to load" in error_msg or "not found" in error_msg:
            print("✓ material_set_texture properly handles invalid texture path")
        else:
            raise
