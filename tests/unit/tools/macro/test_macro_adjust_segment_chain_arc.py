from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self):
        self.boxes = {
            "Tail_01": {
                "object_name": "Tail_01",
                "center": [0.0, 0.0, 0.0],
                "dimensions": [0.4, 0.4, 0.4],
            },
            "Tail_02": {
                "object_name": "Tail_02",
                "center": [1.0, 0.0, 0.0],
                "dimensions": [0.4, 0.4, 0.4],
            },
            "Tail_03": {
                "object_name": "Tail_03",
                "center": [2.0, 0.0, 0.0],
                "dimensions": [0.4, 0.4, 0.4],
            },
        }
        self.inspect_payload = {
            name: {"rotation": [0.0, 0.0, 0.0]}
            for name in self.boxes
        }

    def get_bounding_box(self, object_name, world_space=True):
        box = self.boxes[object_name]
        center = box["center"]
        half = [value / 2.0 for value in box["dimensions"]]
        return {
            "object_name": object_name,
            "center": list(center),
            "dimensions": list(box["dimensions"]),
            "min": [center[idx] - half[idx] for idx in range(3)],
            "max": [center[idx] + half[idx] for idx in range(3)],
        }

    def inspect_object(self, object_name):
        return self.inspect_payload[object_name]


class FakeModelingTool:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def transform_object(self, name, location=None, rotation=None, scale=None):
        self.calls.append(
            ("transform_object", {"name": name, "location": location, "rotation": rotation, "scale": scale})
        )
        return f"Transformed object '{name}'"


def test_macro_adjust_segment_chain_arc_places_segments_along_arc():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    result = handler.adjust_segment_chain_arc(
        segment_objects=["Tail_01", "Tail_02", "Tail_03"],
        rotation_axis="Y",
        total_angle=60.0,
        direction="positive",
        apply_rotation=True,
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_adjust_segment_chain_arc"
    assert result["objects_modified"] == ["Tail_02", "Tail_03"]
    assert len(modeling.calls) == 2
    assert modeling.calls[0][1]["location"] == pytest.approx([0.866025, 0.0, -0.5], abs=1e-5)
    assert modeling.calls[1][1]["location"] == pytest.approx([1.366025, 0.0, -1.366025], abs=1e-5)
    assert modeling.calls[0][1]["rotation"][1] == pytest.approx(0.523599, abs=1e-6)
    assert modeling.calls[1][1]["rotation"][1] == pytest.approx(1.047198, abs=1e-6)


def test_macro_adjust_segment_chain_arc_requires_two_segments():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    with pytest.raises(ValueError, match="segment_objects must contain at least 2 object names"):
        handler.adjust_segment_chain_arc(segment_objects=["Tail_01"])
