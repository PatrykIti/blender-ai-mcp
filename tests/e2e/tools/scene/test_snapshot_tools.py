"""
E2E Tests for Snapshot Tools (TASK-014-4)

These tests require a running Blender instance with the addon loaded.
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


def test_snapshot_state(scene_handler):
    """Test creating a scene snapshot."""
    try:
        result = scene_handler.snapshot_state(
            include_mesh_stats=False,
            include_materials=False
        )

        assert isinstance(result, dict)
        assert "hash" in result
        assert "snapshot" in result

        snapshot = result["snapshot"]
        assert "timestamp" in snapshot
        assert "object_count" in snapshot
        assert "objects" in snapshot
        assert "mode" in snapshot

        # Validate hash is non-empty
        assert len(result["hash"]) == 64  # SHA256 hash length

        print(f"✓ snapshot_state: captured {snapshot['object_count']} objects, hash={result['hash'][:8]}...")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_snapshot_state_with_options(scene_handler):
    """Test snapshot with mesh stats and materials."""
    try:
        result = scene_handler.snapshot_state(
            include_mesh_stats=True,
            include_materials=True
        )

        assert isinstance(result, dict)
        assert "snapshot" in result

        snapshot = result["snapshot"]
        objects = snapshot.get("objects", [])

        # Check if any mesh object has mesh_stats
        has_mesh_stats = any("mesh_stats" in obj for obj in objects)
        has_materials = any("materials" in obj for obj in objects)

        print(f"✓ snapshot_state (full): mesh_stats={has_mesh_stats}, materials={has_materials}")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_snapshot_hash_consistency(scene_handler):
    """Test that identical scenes produce identical hashes."""
    try:
        result1 = scene_handler.snapshot_state()
        result2 = scene_handler.snapshot_state()

        # Hashes should be identical if scene didn't change
        assert result1["hash"] == result2["hash"], "Snapshot hashes should be consistent"

        print(f"✓ snapshot hash consistency: {result1['hash'][:8]}... == {result2['hash'][:8]}...")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
