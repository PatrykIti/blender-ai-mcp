from __future__ import annotations

import pytest
from server.application.services.spatial_graph import SpatialGraphService


class FakeReader:
    def __init__(self) -> None:
        self.boxes = {
            "Body": {
                "min": [-1.0, -1.0, 0.0],
                "max": [1.0, 1.0, 2.0],
                "center": [0.0, 0.0, 1.0],
                "dimensions": [2.0, 2.0, 2.0],
            },
            "Base": {
                "min": [-2.0, -2.0, -0.5],
                "max": [2.0, 2.0, 0.0],
                "center": [0.0, 0.0, -0.25],
                "dimensions": [4.0, 4.0, 0.5],
            },
            "Wheel_L": {
                "min": [-2.5, -0.5, 0.0],
                "max": [-1.5, 0.5, 1.0],
                "center": [-2.0, 0.0, 0.5],
                "dimensions": [1.0, 1.0, 1.0],
            },
            "Wheel_R": {
                "min": [1.5, -0.5, 0.0],
                "max": [2.5, 0.5, 1.0],
                "center": [2.0, 0.0, 0.5],
                "dimensions": [1.0, 1.0, 1.0],
            },
        }

    def get_bounding_box(self, object_name: str, world_space: bool = True) -> dict:
        payload = self.boxes[object_name]
        return {"object_name": object_name, **payload}

    def list_objects(self) -> list[dict]:
        return [{"name": name, "type": "MESH"} for name in self.boxes]

    def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001) -> dict:
        if {from_object, to_object} == {"Body", "Base"}:
            return {
                "from_object": from_object,
                "to_object": to_object,
                "gap": 0.0,
                "axis_gap": {"x": 0.0, "y": 0.0, "z": 0.0},
                "relation": "contact",
                "tolerance": tolerance,
                "units": "blender_units",
            }
        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": 0.2,
            "axis_gap": {"x": 0.2, "y": 0.0, "z": 0.0},
            "relation": "separated",
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def measure_alignment(
        self,
        from_object: str,
        to_object: str,
        axes: list[str] | None = None,
        reference: str = "CENTER",
        tolerance: float = 0.0001,
    ) -> dict:
        if {from_object, to_object} == {"Wheel_L", "Wheel_R"}:
            return {
                "from_object": from_object,
                "to_object": to_object,
                "reference": reference,
                "axes": axes or ["X", "Y", "Z"],
                "deltas": {"x": -4.0, "y": 0.0, "z": 0.0},
                "aligned_axes": ["Y", "Z"],
                "misaligned_axes": ["X"],
                "is_aligned": False,
                "tolerance": tolerance,
                "units": "blender_units",
            }
        return {
            "from_object": from_object,
            "to_object": to_object,
            "reference": reference,
            "axes": axes or ["X", "Y", "Z"],
            "deltas": {"x": 0.0, "y": 0.0, "z": 0.0},
            "aligned_axes": ["X", "Y", "Z"],
            "misaligned_axes": [],
            "is_aligned": True,
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001) -> dict:
        return {
            "from_object": from_object,
            "to_object": to_object,
            "overlaps": False,
            "touching": False,
            "relation": "disjoint",
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def assert_contact(
        self, from_object: str, to_object: str, max_gap: float = 0.0001, allow_overlap: bool = False
    ) -> dict:
        if {from_object, to_object} == {"Body", "Base"}:
            return {
                "assertion": "scene_assert_contact",
                "passed": True,
                "subject": from_object,
                "target": to_object,
                "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
                "actual": {"gap": 0.0, "relation": "contact"},
            }
        return {
            "assertion": "scene_assert_contact",
            "passed": False,
            "subject": from_object,
            "target": to_object,
            "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
            "actual": {"gap": 0.2, "relation": "separated"},
        }

    def assert_symmetry(
        self,
        left_object: str,
        right_object: str,
        axis: str = "X",
        mirror_coordinate: float = 0.0,
        tolerance: float = 0.0001,
    ) -> dict:
        return {
            "assertion": "scene_assert_symmetry",
            "passed": True,
            "subject_left": left_object,
            "subject_right": right_object,
            "axis": axis,
            "mirror_coordinate": mirror_coordinate,
            "tolerance": tolerance,
        }


def test_build_relation_graph_preserves_support_semantics_on_primary_pair_collision():
    service = SpatialGraphService()
    reader = FakeReader()

    relation_graph = service.build_relation_graph(
        reader=reader,
        scope_graph={
            "scope_kind": "object_set",
            "primary_target": "Body",
            "object_names": ["Body", "Base"],
            "object_count": 2,
            "object_roles": [
                {"object_name": "Body", "role": "anchor_core"},
                {"object_name": "Base", "role": "support_base"},
            ],
        },
        goal_hint="support",
        include_truth_payloads=False,
        include_guided_pairs=True,
    )

    assert relation_graph["summary"]["support_pairs"] == 1
    assert relation_graph["summary"]["failing_pairs"] == 0
    assert relation_graph["pairs"][0]["pair_source"] == "primary_to_other"
    assert relation_graph["pairs"][0]["support_semantics"] is not None
    assert relation_graph["pairs"][0]["support_semantics"]["verdict"] == "supported"
    assert "support" in relation_graph["pairs"][0]["relation_kinds"]
    assert "supported" in relation_graph["pairs"][0]["relation_verdicts"]


def test_build_relation_graph_does_not_count_healthy_symmetry_pair_as_failure():
    service = SpatialGraphService()
    reader = FakeReader()

    relation_graph = service.build_relation_graph(
        reader=reader,
        scope_graph={
            "scope_kind": "object_set",
            "primary_target": "Wheel_L",
            "object_names": ["Wheel_L", "Wheel_R"],
            "object_count": 2,
            "object_roles": [
                {"object_name": "Wheel_L", "role": "anchor_core"},
                {"object_name": "Wheel_R", "role": "structural_peer"},
            ],
        },
        goal_hint="symmetry",
        include_truth_payloads=False,
        include_guided_pairs=True,
    )

    assert relation_graph["summary"]["symmetry_pairs"] == 1
    assert relation_graph["summary"]["failing_pairs"] == 0
    assert relation_graph["pairs"][0]["symmetry_semantics"] is not None
    assert relation_graph["pairs"][0]["symmetry_semantics"]["verdict"] == "symmetric"
    assert "symmetry" in relation_graph["pairs"][0]["relation_kinds"]
    assert "symmetric" in relation_graph["pairs"][0]["relation_verdicts"]


def test_build_scope_graph_rejects_missing_explicit_target_object():
    service = SpatialGraphService()
    reader = FakeReader()

    with pytest.raises(ValueError, match="Object\\(s\\) not found in scene: 'Boddy'"):
        service.build_scope_graph(
            reader=reader,
            target_object="Boddy",
            target_objects=None,
            collection_name=None,
        )
