"""
Tests for Snapshot Tools (TASK-014-4, 014-5)
"""
import pytest
import json
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.services.snapshot_diff import get_snapshot_diff_service
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


def test_compare_snapshot_identical():
    """Test comparing identical snapshots."""
    diff_service = get_snapshot_diff_service()

    snapshot_data = {
        "hash": "abc123",
        "snapshot": {
            "timestamp": "2025-01-01T00:00:00Z",
            "object_count": 1,
            "objects": [
                {
                    "name": "Cube",
                    "type": "MESH",
                    "location": [0, 0, 0],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1]
                }
            ]
        }
    }

    snapshot_str = json.dumps(snapshot_data)

    result = diff_service.compare_snapshots(
        baseline_snapshot=snapshot_str,
        target_snapshot=snapshot_str,
        ignore_minor_transforms=0.0
    )

    assert result["has_changes"] == False
    assert len(result["objects_added"]) == 0
    assert len(result["objects_removed"]) == 0
    assert len(result["objects_modified"]) == 0

    print("✓ compare_snapshot: identical snapshots have no changes")


def test_compare_snapshot_with_changes():
    """Test comparing snapshots with changes."""
    diff_service = get_snapshot_diff_service()

    baseline = {
        "snapshot": {
            "timestamp": "2025-01-01T00:00:00Z",
            "objects": [
                {"name": "Cube", "type": "MESH", "location": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
            ]
        }
    }

    target = {
        "snapshot": {
            "timestamp": "2025-01-01T00:01:00Z",
            "objects": [
                {"name": "Cube", "type": "MESH", "location": [1, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]},
                {"name": "Sphere", "type": "MESH", "location": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
            ]
        }
    }

    result = diff_service.compare_snapshots(
        baseline_snapshot=json.dumps(baseline),
        target_snapshot=json.dumps(target),
        ignore_minor_transforms=0.0
    )

    assert result["has_changes"] == True
    assert "Sphere" in result["objects_added"]
    assert len(result["objects_modified"]) == 1
    assert result["objects_modified"][0]["object_name"] == "Cube"

    print(f"✓ compare_snapshot: detected changes (+{len(result['objects_added'])}, ~{len(result['objects_modified'])})")
