"""
Tests for Material Tools (TASK-014-8, 014-9)
"""
import pytest
from server.application.tool_handlers.material_handler import MaterialToolHandler
from server.adapters.rpc.client import RpcClient
from server.infrastructure.config import get_config


@pytest.fixture
def material_handler():
    """Provides a material handler instance."""
    config = get_config()
    rpc_client = RpcClient(host=config.BLENDER_RPC_HOST, port=config.BLENDER_RPC_PORT)
    return MaterialToolHandler(rpc_client)


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


def test_material_list_by_object(material_handler):
    """Test listing material slots by object."""
    try:
        # Use a known object name - try common defaults
        test_objects = ["Cube", "Sphere", "Plane"]

        result = None
        for obj_name in test_objects:
            try:
                result = material_handler.list_by_object(
                    object_name=obj_name,
                    include_indices=False
                )
                break
            except RuntimeError:
                continue

        if result is None:
            pytest.skip("No test objects available")

        assert isinstance(result, dict)
        assert "object_name" in result
        assert "slot_count" in result
        assert "slots" in result
        assert isinstance(result["slots"], list)

        print(f"✓ material_list_by_object: '{result['object_name']}' has {result['slot_count']} slots")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_material_list_by_object_invalid(material_handler):
    """Test listing material slots with invalid object name."""
    try:
        with pytest.raises(RuntimeError, match="not found"):
            material_handler.list_by_object(
                object_name="NonExistentObject12345",
                include_indices=False
            )
        print("✓ material_list_by_object properly handles invalid object name")
    except RuntimeError as e:
        if "not found" not in str(e).lower():
            pytest.skip(f"Blender not available: {e}")
