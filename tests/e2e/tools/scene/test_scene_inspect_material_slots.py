"""
Tests for Scene Inspect Material Slots (TASK-014-10)
"""
import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.adapters.rpc.client import RpcClient
from server.infrastructure.config import get_config


@pytest.fixture
def scene_handler():
    """Provides a scene handler instance."""
    config = get_config()
    rpc_client = RpcClient(host=config.BLENDER_RPC_HOST, port=config.BLENDER_RPC_PORT)
    return SceneToolHandler(rpc_client)


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


def test_inspect_material_slots_with_filter(scene_handler):
    """Test filtering by material name."""
    try:
        # First get all materials to know what's available
        all_result = scene_handler.inspect_material_slots(
            material_filter=None,
            include_empty_slots=False
        )

        if not all_result["slots"]:
            pytest.skip("No assigned material slots available for filter test")

        # Get first material name
        test_material = all_result["slots"][0]["material_name"]

        # Now filter by that material
        filtered_result = scene_handler.inspect_material_slots(
            material_filter=test_material,
            include_empty_slots=True
        )

        assert isinstance(filtered_result, dict)
        # All returned slots should use the filtered material
        for slot in filtered_result["slots"]:
            assert slot["material_name"] == test_material, f"Found slot with wrong material: {slot['material_name']}"

        print(f"✓ inspect_material_slots (filter '{test_material}'): {len(filtered_result['slots'])} slots")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


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
