"""
Unit tests for Snapshot Diff Service (TASK-014-5)

These tests verify the local snapshot comparison logic without requiring Blender.
"""
import pytest
import json
from server.application.services.snapshot_diff import get_snapshot_diff_service


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


def test_compare_snapshot_object_removed():
    """Test detecting removed objects."""
    diff_service = get_snapshot_diff_service()

    baseline = {
        "snapshot": {
            "objects": [
                {"name": "Cube", "type": "MESH", "location": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]},
                {"name": "Sphere", "type": "MESH", "location": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
            ]
        }
    }

    target = {
        "snapshot": {
            "objects": [
                {"name": "Cube", "type": "MESH", "location": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
            ]
        }
    }

    result = diff_service.compare_snapshots(
        baseline_snapshot=json.dumps(baseline),
        target_snapshot=json.dumps(target),
        ignore_minor_transforms=0.0
    )

    assert result["has_changes"] == True
    assert "Sphere" in result["objects_removed"]


def test_compare_snapshot_ignore_minor_transforms():
    """Test ignoring minor transform differences."""
    diff_service = get_snapshot_diff_service()

    baseline = {
        "snapshot": {
            "objects": [
                {"name": "Cube", "type": "MESH", "location": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
            ]
        }
    }

    target = {
        "snapshot": {
            "objects": [
                {"name": "Cube", "type": "MESH", "location": [0.001, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
            ]
        }
    }

    # With threshold of 0.01, small change should be ignored
    result = diff_service.compare_snapshots(
        baseline_snapshot=json.dumps(baseline),
        target_snapshot=json.dumps(target),
        ignore_minor_transforms=0.01
    )

    assert result["has_changes"] == False
