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
                "min": [-0.1, -0.2, 0.0],
                "max": [0.1, 0.2, 0.6],
                "center": [0.0, 0.0, 0.3],
                "dimensions": [0.2, 0.4, 0.6],
            },
            "Snout": {
                "object_name": "Snout",
                "min": [-0.4, -0.25, -0.2],
                "max": [0.4, 0.25, 0.2],
                "center": [0.0, 0.0, 0.0],
                "dimensions": [0.8, 0.5, 0.4],
            },
            "Nose": {
                "object_name": "Nose",
                "min": [-0.08, -0.08, -0.08],
                "max": [0.08, 0.08, 0.08],
                "center": [0.0, 0.0, 0.0],
                "dimensions": [0.16, 0.16, 0.16],
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
        gap_axes = {}
        for axis_name, index in {"X": 0, "Y": 1, "Z": 2}.items():
            gap_axes[axis_name.lower()] = round(
                max(
                    float(left["min"][index]) - float(right["max"][index]),
                    float(right["min"][index]) - float(left["max"][index]),
                    0.0,
                ),
                6,
            )
        gap = max(gap_axes.values())
        overlap_dimensions = [
            max(
                0.0,
                min(float(left["max"][idx]), float(right["max"][idx]))
                - max(float(left["min"][idx]), float(right["min"][idx])),
            )
            for idx in range(3)
        ]
        if gap <= tolerance:
            relation = "overlapping" if all(value > tolerance for value in overlap_dimensions) else "contact"
        else:
            relation = "separated"
        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": round(gap, 6),
            "axis_gap": gap_axes,
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
        relation = "overlap" if overlaps else "disjoint"
        return {
            "from_object": from_object,
            "to_object": to_object,
            "overlaps": overlaps,
            "touching": self.measure_gap(from_object, to_object, tolerance)["relation"] == "contact",
            "relation": relation,
            "overlap_dimensions": [round(value, 6) for value in overlap_dimensions],
            "overlap_volume": round(overlap_dimensions[0] * overlap_dimensions[1] * overlap_dimensions[2], 6)
            if overlaps
            else 0.0,
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
        if location is not None:
            self.scene.set_center(name, location)
        return f"Transformed object '{name}'"


def test_macro_attach_part_to_surface_seats_part_on_requested_surface():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.attach_part_to_surface(
        part_object="Ear",
        surface_object="Head",
        surface_axis="X",
        surface_side="positive",
        align_mode="center",
        gap=0.0,
        offset=[0.0, 0.1, -0.05],
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_attach_part_to_surface"
    assert result["objects_modified"] == ["Ear"]
    assert result["requires_followup"] is True
    assert modeling.calls[0][0] == "transform_object"
    assert modeling.calls[0][1]["name"] == "Ear"
    assert modeling.calls[0][1]["location"] == pytest.approx([1.1, 0.1, 0.95], abs=1e-9)
    assert any(item["tool_name"] == "scene_measure_gap" for item in result["verification_recommended"])
    assert any(item["tool_name"] == "scene_assert_contact" for item in result["verification_recommended"])
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"


def test_macro_attach_part_to_surface_seats_nose_on_snout_surface():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)
    scene.set_center("Snout", [0.0, 0.0, 1.0])
    scene.set_center("Nose", [2.0, 2.0, 2.0])

    result = handler.attach_part_to_surface(
        part_object="Nose",
        surface_object="Snout",
        surface_axis="X",
        surface_side="positive",
        align_mode="center",
        gap=0.0,
    )

    assert result["status"] == "success"
    assert modeling.calls[0][1]["location"] == pytest.approx([0.48, 0.0, 1.0], abs=1e-9)
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"


def test_macro_attach_part_to_surface_rejects_negative_gap():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    with pytest.raises(ValueError, match="gap must be >= 0"):
        handler.attach_part_to_surface(
            part_object="Ear",
            surface_object="Head",
            surface_axis="X",
            gap=-0.01,
        )


def test_macro_attach_part_to_surface_reports_partial_when_part_is_still_detached():
    scene = FakeSceneTool()

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
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.attach_part_to_surface(
        part_object="Ear",
        surface_object="Head",
        surface_axis="X",
        surface_side="positive",
        align_mode="center",
        gap=0.0,
    )

    assert result["status"] == "partial"
    assert "still not seated/attached correctly" in (result["error"] or "")
    assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "floating_gap"
