"""Service for comparing scene snapshots."""
import json
from typing import Dict, Any, List, Optional


class SnapshotDiffService:
    """Service for computing diffs between scene snapshots."""

    def compare_snapshots(
        self,
        baseline_snapshot: str,
        target_snapshot: str,
        ignore_minor_transforms: float = 0.0
    ) -> Dict[str, Any]:
        """
        Compares two scene snapshots and returns a structured diff.

        Args:
            baseline_snapshot: JSON string of the baseline snapshot
            target_snapshot: JSON string of the target snapshot
            ignore_minor_transforms: Threshold for ignoring small transform changes

        Returns:
            Dictionary with added, removed, and modified objects
        """
        try:
            baseline = json.loads(baseline_snapshot)
            target = json.loads(target_snapshot)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid snapshot JSON: {e}")

        # Extract snapshot data
        baseline_data = baseline.get("snapshot", baseline)
        target_data = target.get("snapshot", target)

        baseline_objects = {
            obj["name"]: obj
            for obj in baseline_data.get("objects", [])
        }
        target_objects = {
            obj["name"]: obj
            for obj in target_data.get("objects", [])
        }

        # Compute differences
        baseline_names = set(baseline_objects.keys())
        target_names = set(target_objects.keys())

        added = target_names - baseline_names
        removed = baseline_names - target_names
        common = baseline_names & target_names

        # Check for modifications
        modified = []
        for name in common:
            baseline_obj = baseline_objects[name]
            target_obj = target_objects[name]

            changes = self._compute_object_changes(
                baseline_obj,
                target_obj,
                ignore_minor_transforms
            )

            if changes:
                modified.append({
                    "object_name": name,
                    "changes": changes
                })

        return {
            "objects_added": sorted(list(added)),
            "objects_removed": sorted(list(removed)),
            "objects_modified": modified,
            "baseline_hash": baseline.get("hash", "unknown"),
            "target_hash": target.get("hash", "unknown"),
            "baseline_timestamp": baseline_data.get("timestamp", "unknown"),
            "target_timestamp": target_data.get("timestamp", "unknown"),
            "has_changes": len(added) > 0 or len(removed) > 0 or len(modified) > 0
        }

    def _compute_object_changes(
        self,
        baseline_obj: Dict[str, Any],
        target_obj: Dict[str, Any],
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Computes detailed changes between two object states."""
        changes = []

        # Check type change
        if baseline_obj.get("type") != target_obj.get("type"):
            changes.append({
                "property": "type",
                "old_value": baseline_obj.get("type"),
                "new_value": target_obj.get("type")
            })

        # Check transform changes
        for prop in ["location", "rotation", "scale"]:
            baseline_val = baseline_obj.get(prop, [])
            target_val = target_obj.get(prop, [])

            if self._vectors_differ(baseline_val, target_val, threshold):
                changes.append({
                    "property": prop,
                    "old_value": baseline_val,
                    "new_value": target_val
                })

        # Check parent change
        if baseline_obj.get("parent") != target_obj.get("parent"):
            changes.append({
                "property": "parent",
                "old_value": baseline_obj.get("parent"),
                "new_value": target_obj.get("parent")
            })

        # Check visibility change
        if baseline_obj.get("visible") != target_obj.get("visible"):
            changes.append({
                "property": "visible",
                "old_value": baseline_obj.get("visible"),
                "new_value": target_obj.get("visible")
            })

        # Check modifier changes
        baseline_mods = baseline_obj.get("modifiers", [])
        target_mods = target_obj.get("modifiers", [])

        if len(baseline_mods) != len(target_mods) or \
           [m.get("type") for m in baseline_mods] != [m.get("type") for m in target_mods]:
            changes.append({
                "property": "modifiers",
                "old_value": [m.get("type") for m in baseline_mods],
                "new_value": [m.get("type") for m in target_mods]
            })

        # Check material changes (if present)
        baseline_mats = baseline_obj.get("materials", [])
        target_mats = target_obj.get("materials", [])

        if baseline_mats != target_mats:
            changes.append({
                "property": "materials",
                "old_value": baseline_mats,
                "new_value": target_mats
            })

        return changes

    def _vectors_differ(
        self,
        vec1: List[float],
        vec2: List[float],
        threshold: float
    ) -> bool:
        """Checks if two vectors differ by more than threshold."""
        if len(vec1) != len(vec2):
            return True

        for v1, v2 in zip(vec1, vec2):
            if abs(v1 - v2) > threshold:
                return True

        return False


# Global singleton instance
_snapshot_diff_service = None


def get_snapshot_diff_service() -> SnapshotDiffService:
    """Returns the global snapshot diff service instance."""
    global _snapshot_diff_service
    if _snapshot_diff_service is None:
        _snapshot_diff_service = SnapshotDiffService()
    return _snapshot_diff_service
