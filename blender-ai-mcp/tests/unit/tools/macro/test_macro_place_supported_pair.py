from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self):
        self.boxes = {
            "Floor": {
                "object_name": "Floor",
                "min": [-3.0, -2.0, -0.1],
                "max": [3.0, 2.0, 0.1],
                "center": [0.0, 0.0, 0.0],
                "dimensions": [6.0, 4.0, 0.2],
            },
            "Foot_L": {
                "object_name": "Foot_L",
                "min": [-1.4, -0.3, 0.5],
                "max": [-1.0, 0.3, 1.0],
                "center": [-1.2, 0.0, 0.75],
                "dimensions": [0.4, 0.6, 0.5],
            },
            "Foot_R": {
                "object_name": "Foot_R",
                "min": [1.35, -0.25, 0.65],
                "max": [1.75, 0.35, 1.15],
                "center": [1.55, 0.05, 0.9],
                "dimensions": [0.4, 0.6, 0.5],
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
        for axis_name, index in {"X": 0, "Y": 1, "Z": 2}.items():
            axis_gap[axis_name.lower()] = round(
                max(
                    float(left["min"][index]) - float(right["max"][index]),
                    float(right["min"][index]) - float(left["max"][index]),
                    0.0,
                ),
                6,
            )
        gap_value = max(axis_gap.values())
        relation = "contact" if gap_value <= tolerance else "separated"
        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": gap_value,
            "axis_gap": axis_gap,
            "relation": relation,
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def assert_contact(self, from_object, to_object, max_gap=0.001, allow_overlap=False):
        gap = self.measure_gap(from_object, to_object, max_gap)
        return {
            "assertion": "scene_assert_contact",
            "passed": gap["relation"] == "contact",
            "subject": from_object,
            "target": to_object,
            "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
            "actual": {"gap": gap["gap"], "relation": gap["relation"]},
            "delta": {"gap_overage": max(0.0, gap["gap"] - max_gap)},
            "tolerance": max_gap,
            "units": "blender_units",
        }

    def assert_symmetry(self, left_object, right_object, axis="X", mirror_coordinate=0.0, tolerance=0.0001):
        left = self.boxes[left_object]
        right = self.boxes[right_object]
        axis_index = {"X": 0, "Y": 1, "Z": 2}[axis]
        expected = (2.0 * float(mirror_coordinate)) - float(left["center"][axis_index])
        mirror_delta = round(float(right["center"][axis_index]) - expected, 6)
        passed = abs(mirror_delta) <= tolerance and all(
            abs(float(left["center"][idx]) - float(right["center"][idx])) <= tolerance
            for idx in range(3)
            if idx != axis_index
        )
        return {
            "assertion": "scene_assert_symmetry",
            "passed": passed,
            "subject": left_object,
            "target": right_object,
            "expected": {"axis": axis, "mirror_coordinate": mirror_coordinate},
            "actual": {"left_center": left["center"], "right_center": right["center"]},
            "delta": {"mirror_axis": mirror_delta},
            "tolerance": tolerance,
            "units": "blender_units",
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


def test_macro_place_supported_pair_places_mirrored_pair_on_shared_support():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.place_supported_pair(
        left_object="Foot_L",
        right_object="Foot_R",
        support_object="Floor",
        axis="X",
        mirror_coordinate=0.0,
        support_axis="Z",
        support_side="positive",
        anchor_object="left",
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_place_supported_pair"
    assert modeling.calls[0][1]["name"] == "Foot_L"
    assert modeling.calls[0][1]["location"] == pytest.approx([-1.2, 0.0, 0.35], abs=1e-9)
    assert modeling.calls[1][1]["name"] == "Foot_R"
    assert modeling.calls[1][1]["location"] == pytest.approx([1.2, 0.0, 0.35], abs=1e-9)
    assert result["actions_taken"][2]["action"] == "plan_supported_pair"
    assert result["actions_taken"][-2]["details"]["passed"] is True
    assert result["actions_taken"][-1]["details"]["support_checks"]["Foot_L"]["contact_assertion"]["passed"] is True
    assert result["actions_taken"][-1]["details"]["support_checks"]["Foot_R"]["contact_assertion"]["passed"] is True


def test_macro_place_supported_pair_blocks_when_support_breaks_pair_symmetry():
    scene = FakeSceneTool()
    scene.boxes["Foot_R"] = {
        "object_name": "Foot_R",
        "min": [1.35, -0.25, 0.4],
        "max": [1.75, 0.35, 1.4],
        "center": [1.55, 0.05, 0.9],
        "dimensions": [0.4, 0.6, 1.0],
    }
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.place_supported_pair(
        left_object="Foot_L",
        right_object="Foot_R",
        support_object="Floor",
        axis="X",
        mirror_coordinate=0.0,
        support_axis="Z",
        support_side="positive",
        tolerance=0.05,
    )

    assert result["status"] == "blocked"
    assert result["macro_name"] == "macro_place_supported_pair"
    assert modeling.calls == []
    assert "different Z coordinates" in (result["error"] or "")
