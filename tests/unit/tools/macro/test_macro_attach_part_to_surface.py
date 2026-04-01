from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def get_bounding_box(self, object_name, world_space=True):
        if object_name == "Head":
            return {
                "object_name": object_name,
                "min": [-1.0, -1.0, 0.0],
                "max": [1.0, 1.0, 2.0],
                "center": [0.0, 0.0, 1.0],
                "dimensions": [2.0, 2.0, 2.0],
            }
        return {
            "object_name": object_name,
            "min": [-0.1, -0.2, 0.0],
            "max": [0.1, 0.2, 0.6],
            "center": [0.0, 0.0, 0.3],
            "dimensions": [0.2, 0.4, 0.6],
        }


class FakeModelingTool:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def transform_object(self, name, location=None, rotation=None, scale=None):
        self.calls.append(
            ("transform_object", {"name": name, "location": location, "rotation": rotation, "scale": scale})
        )
        return f"Transformed object '{name}'"


def test_macro_attach_part_to_surface_seats_part_on_requested_surface():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
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


def test_macro_attach_part_to_surface_rejects_negative_gap():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    with pytest.raises(ValueError, match="gap must be >= 0"):
        handler.attach_part_to_surface(
            part_object="Ear",
            surface_object="Head",
            surface_axis="X",
            gap=-0.01,
        )
