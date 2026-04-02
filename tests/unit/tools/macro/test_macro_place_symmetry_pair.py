from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self):
        self.boxes = {
            "Ear_L": {
                "object_name": "Ear_L",
                "min": [-1.3, -0.2, 0.7],
                "max": [-1.1, 0.2, 1.3],
                "center": [-1.2, 0.0, 1.0],
                "dimensions": [0.2, 0.4, 0.6],
            },
            "Ear_R": {
                "object_name": "Ear_R",
                "min": [1.35, -0.15, 0.75],
                "max": [1.55, 0.25, 1.35],
                "center": [1.45, 0.05, 1.05],
                "dimensions": [0.2, 0.4, 0.6],
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
            "details": {"failed_checks": [] if passed else ["mirror_axis"]},
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


def test_macro_place_symmetry_pair_mirrors_follower_around_requested_plane():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.place_symmetry_pair(
        left_object="Ear_L",
        right_object="Ear_R",
        axis="X",
        mirror_coordinate=0.0,
        anchor_object="left",
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_place_symmetry_pair"
    assert modeling.calls[0][1]["location"] == pytest.approx([1.2, 0.0, 1.0], abs=1e-9)
    assert result["actions_taken"][0]["action"] == "inspect_symmetry_before"
    assert result["actions_taken"][2]["action"] == "place_symmetry_pair"
    assert result["actions_taken"][-1]["details"]["passed"] is True


def test_macro_place_symmetry_pair_auto_anchor_chooses_further_side():
    scene = FakeSceneTool()
    modeling = FakeModelingTool(scene)
    handler = MacroToolHandler(scene, modeling)

    result = handler.place_symmetry_pair(
        left_object="Ear_L",
        right_object="Ear_R",
        axis="X",
        mirror_coordinate=0.0,
        anchor_object="auto",
    )

    assert result["status"] == "success"
    assert result["actions_taken"][1]["details"]["anchor_object"] == "Ear_R"
    assert modeling.calls[0][1]["name"] == "Ear_L"
