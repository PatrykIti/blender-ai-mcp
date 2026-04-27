from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self):
        self.boxes = {
            "Body": {
                "object_name": "Body",
                "min": [-1.0, -1.0, -1.0],
                "max": [1.0, 1.0, 1.0],
                "center": [0.0, 0.0, 0.0],
                "dimensions": [2.0, 2.0, 2.0],
            },
            "Horn": {
                "object_name": "Horn",
                "min": [0.85, -0.2, 0.7],
                "max": [1.05, 0.2, 1.3],
                "center": [0.95, 0.0, 1.0],
                "dimensions": [0.2, 0.4, 0.6],
            },
            "Forelimb": {
                "object_name": "Forelimb",
                "min": [0.7, -0.15, -1.2],
                "max": [1.3, 0.15, -0.8],
                "center": [1.0, 0.0, -1.0],
                "dimensions": [0.6, 0.3, 0.4],
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
        axis_gap = {}
        overlap_dimensions = []
        for axis_name, index in {"X": 0, "Y": 1, "Z": 2}.items():
            gap_value = max(
                float(left["min"][index]) - float(right["max"][index]),
                float(right["min"][index]) - float(left["max"][index]),
                0.0,
            )
            axis_gap[axis_name.lower()] = round(gap_value, 6)
            overlap_dimensions.append(
                max(
                    0.0,
                    min(float(left["max"][index]), float(right["max"][index]))
                    - max(float(left["min"][index]), float(right["min"][index])),
                )
            )
        gap_value = max(axis_gap.values())
        if gap_value <= tolerance:
            if all(value > tolerance for value in overlap_dimensions):
                relation = "overlapping"
            else:
                relation = "contact"
        else:
            relation = "separated"
        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": round(gap_value, 6),
            "axis_gap": axis_gap,
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
        left = self.boxes[from_object]
        right = self.boxes[to_object]
        intersection_min = [max(float(left["min"][idx]), float(right["min"][idx])) for idx in range(3)]
        intersection_max = [min(float(left["max"][idx]), float(right["max"][idx])) for idx in range(3)]
        overlap_dimensions = [max(0.0, intersection_max[idx] - intersection_min[idx]) for idx in range(3)]
        overlaps = all(value > tolerance for value in overlap_dimensions)
        touching = not overlaps and self.measure_gap(from_object, to_object, tolerance)["relation"] == "contact"
        relation = "overlap" if overlaps else ("touching" if touching else "disjoint")
        overlap_volume = overlap_dimensions[0] * overlap_dimensions[1] * overlap_dimensions[2] if overlaps else 0.0
        return {
            "from_object": from_object,
            "to_object": to_object,
            "overlaps": overlaps,
            "touching": touching,
            "relation": relation,
            "overlap_dimensions": [round(value, 6) for value in overlap_dimensions],
            "overlap_volume": round(overlap_volume, 6),
            "intersection_min": [round(value, 6) for value in intersection_min] if overlaps else None,
            "intersection_max": [round(value, 6) for value in intersection_max] if overlaps else None,
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def assert_contact(self, from_object, to_object, max_gap=0.001, allow_overlap=False):
        gap = self.measure_gap(from_object, to_object, max_gap)
        overlaps = gap["relation"] == "overlapping"
        passed = gap["gap"] <= max_gap and (allow_overlap or not overlaps)
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
            "details": {
                "axis_gap": gap["axis_gap"],
                "measured_relation": gap["relation"],
                "overlap_rejected": overlaps,
            },
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


def test_macro_cleanup_part_intersections_pushes_overlap_to_contact():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.cleanup_part_intersections(
        part_object="Horn",
        reference_object="Body",
        gap=0.0,
        max_push=0.3,
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_cleanup_part_intersections"
    assert modeling.calls[0][1]["location"] == pytest.approx([1.1, 0.0, 1.0], abs=1e-9)
    assert result["actions_taken"][1]["action"] == "plan_intersection_cleanup"
    assert result["actions_taken"][-2]["details"]["overlap"]["overlaps"] is False
    assert result["actions_taken"][-2]["details"]["contact_assertion"]["passed"] is True
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"


def test_macro_cleanup_part_intersections_blocks_when_push_exceeds_bound():
    scene = FakeSceneTool()
    scene.set_center("Horn", [0.7, 0.0, 1.0])
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.cleanup_part_intersections(
        part_object="Horn",
        reference_object="Body",
        max_push=0.1,
    )

    assert result["status"] == "blocked"
    assert modeling.calls == []
    assert "exceeds max_push" in (result["error"] or "")


def test_macro_cleanup_part_intersections_pushes_forelimb_body_overlap_to_contact():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.cleanup_part_intersections(
        part_object="Forelimb",
        reference_object="Body",
        gap=0.0,
        max_push=0.3,
    )

    assert result["status"] == "success"
    assert modeling.calls[0][1]["location"] == pytest.approx([1.0, 0.0, -1.2], abs=1e-9)
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"


def test_macro_cleanup_part_intersections_noops_when_pair_is_already_disjoint():
    scene = FakeSceneTool()
    scene.set_center("Horn", [1.3, 0.0, 1.0])
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.cleanup_part_intersections(
        part_object="Horn",
        reference_object="Body",
    )

    assert result["status"] == "success"
    assert result["objects_modified"] is None
    assert modeling.calls == []
    assert result["requires_followup"] is False


def test_macro_cleanup_part_intersections_reports_partial_when_pair_is_still_detached():
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

    result = handler.cleanup_part_intersections(
        part_object="Horn",
        reference_object="Body",
        gap=0.0,
        max_push=0.3,
    )

    assert result["status"] == "partial"
    assert "still not seated/attached correctly" in (result["error"] or "")
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "floating_gap"
