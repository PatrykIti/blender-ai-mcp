"""
Tests for Scene Inspect Material Slots (TASK-014-10)
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.material_handler import MaterialToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def material_handler(rpc_client):
    """Provides a material handler instance using shared RPC client."""
    return MaterialToolHandler(rpc_client)


def test_inspect_material_slots_basic(scene_handler):
    """Test basic material slot inspection."""
    try:
        result = scene_handler.inspect_material_slots(
            material_filter=None,
            include_empty_slots=True
        )

        assert isinstance(result, dict)
        assert "total_slots" in result
        assert "assigned_slots" in result
        assert "empty_slots" in result
        assert "warnings" in result
        assert "slots" in result

        print(f"✓ inspect_material_slots: {result['total_slots']} total slots ({result['assigned_slots']} assigned, {result['empty_slots']} empty)")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_inspect_material_slots_exclude_empty(scene_handler):
    """Test excluding empty slots."""
    try:
        result = scene_handler.inspect_material_slots(
            material_filter=None,
            include_empty_slots=False
        )

        assert isinstance(result, dict)
        assert "slots" in result

        # All returned slots should have materials assigned
        for slot in result["slots"]:
            assert slot["material_name"] is not None, "Found empty slot when include_empty_slots=False"
            assert not slot["is_empty"], "Found empty slot when include_empty_slots=False"

        print(f"✓ inspect_material_slots (no empty): {len(result['slots'])} assigned slots")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_inspect_material_slots_with_filter(scene_handler, modeling_handler, material_handler):
    """Test filtering by material name."""
    obj_name = "E2E_MatSlotFilterTest"
    mat_name = "E2E_FilterTestMaterial"
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

        # Create and assign material
        material_handler.create_material(name=mat_name)
        material_handler.assign_material(material_name=mat_name, object_name=obj_name)

        # Now filter by that material
        filtered_result = scene_handler.inspect_material_slots(
            material_filter=mat_name,
            include_empty_slots=True
        )

        assert isinstance(filtered_result, dict)
        assert len(filtered_result["slots"]) > 0, "Expected at least one slot with test material"

        # All returned slots should use the filtered material
        for slot in filtered_result["slots"]:
            assert slot["material_name"] == mat_name, f"Found slot with wrong material: {slot['material_name']}"

        print(f"✓ inspect_material_slots (filter '{mat_name}'): {len(filtered_result['slots'])} slots")

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


def test_inspect_material_slots_warnings(scene_handler):
    """Test warning detection for empty slots."""
    try:
        result = scene_handler.inspect_material_slots(
            material_filter=None,
            include_empty_slots=True
        )

        assert isinstance(result, dict)
        assert "warnings" in result

        # If there are empty slots, there should be warnings
        if result["empty_slots"] > 0:
            assert len(result["warnings"]) > 0, "Expected warnings for empty slots"
            # Check that warnings mention empty slots
            empty_warnings = [w for w in result["warnings"] if "Empty slot" in w]
            assert len(empty_warnings) > 0, "Expected 'Empty slot' warnings"

        print(f"✓ inspect_material_slots warnings: {len(result['warnings'])} warnings detected")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
