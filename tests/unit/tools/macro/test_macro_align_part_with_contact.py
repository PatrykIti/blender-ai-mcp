from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self):
        self.boxes = {
            "Head": {
                "object_name": "Head",
                "min": [-1.0, -1.0, 0.0],
                "max": [1.0, 1.0, 2.0],
                "center": [0.0, 0.0, 1.0],
                "dimensions": [2.0, 2.0, 2.0],
            },
            "Ear": {
                "object_name": "Ear",
                "min": [1.15, -0.2, 0.7],
                "max": [1.35, 0.2, 1.3],
                "center": [1.25, 0.0, 1.0],
                "dimensions": [0.2, 0.4, 0.6],
            },
            "Body": {
                "object_name": "Body",
                "min": [-1.0, -1.0, -1.0],
                "max": [1.0, 1.0, 1.0],
                "center": [0.0, 0.0, 0.0],
                "dimensions": [2.0, 2.0, 2.0],
            },
            "Forelimb": {
                "object_name": "Forelimb",
                "min": [0.7, -0.15, -1.35],
                "max": [1.3, 0.15, -1.05],
                "center": [1.0, 0.0, -1.2],
                "dimensions": [0.6, 0.3, 0.3],
            },
        }

    def get_bounding_box(self, object_name, world_space=True):
        return self.boxes[object_name]

    def set_center(self, object_name, center):
        bbox = self.boxes[object_name]
        half = [value / 2.0 for value in bbox["dimensions"]]
        bbox["center"] = list(center)
        bbox["min"] = [round(center[idx] - half[idx], 6) for idx in range(3)]
        bbox["max"] = [round(center[idx] + half[idx], 6) for idx in range(3)]

    def measure_gap(self, from_object, to_object, tolerance=0.0001):
        left = self.boxes[from_object]
        right = self.boxes[to_object]
        gap_x = max(float(left["min"][0]) - float(right["max"][0]), float(right["min"][0]) - float(left["max"][0]), 0.0)
        relation = "contact" if gap_x <= tolerance else "separated"
        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": round(gap_x, 6),
            "axis_gap": {"x": round(gap_x, 6), "y": 0.0, "z": 0.0},
            "relation": relation,
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def measure_alignment(self, from_object, to_object, axes=None, reference="CENTER", tolerance=0.0001):
        left = self.boxes[from_object]
        right = self.boxes[to_object]
        axis_names = list(axes or ["X", "Y", "Z"])
        deltas = {}
        aligned_axes = []
        misaligned_axes = []
        for axis_name, index in {"X": 0, "Y": 1, "Z": 2}.items():
            if axis_name not in axis_names:
                continue
            delta = round(float(left["center"][index]) - float(right["center"][index]), 6)
            deltas[axis_name.lower()] = delta
            if abs(delta) <= tolerance:
                aligned_axes.append(axis_name)
            else:
                misaligned_axes.append(axis_name)
        return {
            "from_object": from_object,
            "to_object": to_object,
            "reference": reference,
            "axes": axis_names,
            "deltas": deltas,
            "aligned_axes": aligned_axes,
            "misaligned_axes": misaligned_axes,
            "is_aligned": len(misaligned_axes) == 0,
            "max_abs_delta": max((abs(value) for value in deltas.values()), default=0.0),
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def measure_overlap(self, from_object, to_object, tolerance=0.0001):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "overlaps": False,
            "touching": self.measure_gap(from_object, to_object, tolerance)["relation"] == "contact",
            "relation": "disjoint",
            "overlap_dimensions": [0.0, 0.0, 0.0],
            "overlap_volume": 0.0,
            "intersection_min": None,
            "intersection_max": None,
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def assert_contact(self, from_object, to_object, max_gap=0.001, allow_overlap=False):
        gap = self.measure_gap(from_object, to_object, max_gap)
        passed = gap["relation"] == "contact"
        return {
            "assertion": "scene_assert_contact",
            "passed": passed,
            "subject": from_object,
            "target": to_object,
            "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
            "actual": {"gap": gap["gap"], "relation": gap["relation"]},
            "delta": {"gap_overage": max(0.0, gap["gap"] - max_gap)},
            "tolerance": max_gap,
            "units": "blender_units",
            "details": {"axis_gap": gap["axis_gap"], "measured_relation": gap["relation"], "overlap_rejected": False},
        }


class FakeModelingTool:
    def __init__(self, scene):
        self.scene = scene
        self.calls: list[tuple[str, dict]] = []

    def transform_object(self, name, location=None, rotation=None, scale=None):
        self.calls.append(
            ("transform_object", {"name": name, "location": location, "rotation": rotation, "scale": scale})
        )
        self.scene.set_center(name, location)
        return f"Transformed object '{name}'"


def test_macro_align_part_with_contact_inferrs_side_and_repairs_gap():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.align_part_with_contact(
        part_object="Ear",
        reference_object="Head",
        target_relation="contact",
        align_mode="none",
        max_nudge=0.2,
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_align_part_with_contact"
    assert modeling.calls[0][1]["location"] == pytest.approx([1.1, 0.0, 1.0], abs=1e-9)
    assert result["actions_taken"][1]["details"]["normal_axis"] == "X"
    assert result["actions_taken"][1]["details"]["preserved_side"] == "positive"
    assert result["actions_taken"][-2]["details"]["contact_assertion"]["passed"] is True
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"


def test_macro_align_part_with_contact_blocks_when_nudge_exceeds_bound():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.align_part_with_contact(
        part_object="Ear",
        reference_object="Head",
        target_relation="contact",
        align_mode="none",
        max_nudge=0.01,
    )

    assert result["status"] == "blocked"
    assert result["macro_name"] == "macro_align_part_with_contact"
    assert modeling.calls == []
    assert "exceeds max_nudge" in (result["error"] or "")


def test_macro_align_part_with_contact_repairs_forelimb_body_gap_as_attachment():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.align_part_with_contact(
        part_object="Forelimb",
        reference_object="Body",
        target_relation="contact",
        align_mode="none",
        max_nudge=0.2,
    )

    assert result["status"] == "success"
    assert modeling.calls[0][1]["location"] == pytest.approx([1.0, 0.0, -1.15], abs=1e-9)
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"


def test_macro_align_part_with_contact_reports_partial_when_pair_is_still_detached():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    def _assert_contact(from_object, to_object, max_gap=0.001, allow_overlap=False):
        return {
            "assertion": "scene_assert_contact",
            "passed": False,
            "subject": from_object,
            "target": to_object,
            "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
            "actual": {"gap": 0.02, "relation": "separated"},
            "delta": {"gap_overage": 0.019},
            "tolerance": max_gap,
            "units": "blender_units",
            "details": {
                "axis_gap": {"x": 0.02, "y": 0.0, "z": 0.0},
                "measured_relation": "separated",
                "overlap_rejected": False,
            },
        }

    scene.assert_contact = _assert_contact

    result = handler.align_part_with_contact(
        part_object="Ear",
        reference_object="Head",
        target_relation="contact",
        align_mode="none",
        max_nudge=0.2,
    )

    assert result["status"] == "partial"
    assert "still not seated/attached correctly" in (result["error"] or "")
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "floating_gap"


def test_pair_truth_summary_carries_bbox_touching_vs_surface_gap_note():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    original_measure_gap = scene.measure_gap

    def _measure_gap(from_object, to_object, tolerance=0.0001):
        payload = original_measure_gap(from_object, to_object, tolerance)
        payload["measurement_basis"] = "mesh_surface"
        payload["bbox_relation"] = "contact"
        payload["relation"] = "separated"
        payload["gap"] = 0.051
        return payload

    def _assert_contact(from_object, to_object, max_gap=0.001, allow_overlap=False):
        return {
            "assertion": "scene_assert_contact",
            "passed": False,
            "subject": from_object,
            "target": to_object,
            "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
            "actual": {"gap": 0.051, "relation": "separated"},
            "delta": {"gap_overage": 0.05},
            "tolerance": max_gap,
            "units": "blender_units",
            "details": {
                "measurement_basis": "mesh_surface",
                "bbox_relation": "contact",
            },
        }

    scene.measure_gap = _measure_gap
    scene.assert_contact = _assert_contact

    summary = handler._pair_truth_summary("Ear", "Head")

    assert summary["contact_assertion"]["passed"] is False
    assert summary["contact_semantics"] == "Bounding boxes touch, but the measured mesh surfaces still have a real gap."
