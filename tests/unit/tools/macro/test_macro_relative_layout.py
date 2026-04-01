from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def get_bounding_box(self, object_name, world_space=True):
        if object_name == "TableTop":
            return {
                "object_name": object_name,
                "min": [-1.0, -0.5, 1.0],
                "max": [1.0, 0.5, 1.2],
                "center": [0.0, 0.0, 1.1],
                "dimensions": [2.0, 1.0, 0.2],
            }
        return {
            "object_name": object_name,
            "min": [-0.1, -0.1, 0.0],
            "max": [0.1, 0.1, 1.0],
            "center": [0.0, 0.0, 0.5],
            "dimensions": [0.2, 0.2, 1.0],
        }


class FakeModelingTool:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def transform_object(self, name, location=None, rotation=None, scale=None):
        self.calls.append(
            ("transform_object", {"name": name, "location": location, "rotation": rotation, "scale": scale})
        )
        return f"Transformed object '{name}'"


def test_macro_relative_layout_places_object_with_contact_and_corner_alignment():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    result = handler.relative_layout(
        moving_object="Leg",
        reference_object="TableTop",
        x_mode="min",
        y_mode="max",
        contact_axis="Z",
        contact_side="negative",
        gap=0.0,
        offset=[0.1, -0.05, 0.0],
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_relative_layout"
    assert result["objects_modified"] == ["Leg"]
    assert result["requires_followup"] is True
    assert modeling.calls[0][0] == "transform_object"
    assert modeling.calls[0][1]["name"] == "Leg"
    assert modeling.calls[0][1]["location"] == pytest.approx([-0.8, 0.35, 0.5], abs=1e-9)
    assert modeling.calls[0][1]["rotation"] is None
    assert modeling.calls[0][1]["scale"] is None
    assert any(item["tool_name"] == "scene_measure_gap" for item in result["verification_recommended"])
    assert any(item["tool_name"] == "scene_assert_contact" for item in result["verification_recommended"])


def test_macro_relative_layout_recommends_alignment_check_for_centered_axes():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    result = handler.relative_layout(
        moving_object="Leg",
        reference_object="TableTop",
        x_mode="center",
        y_mode="center",
        z_mode="none",
        offset=[0.0, 0.0, 0.0],
    )

    assert result["status"] == "success"
    assert modeling.calls[0][1]["location"] == [0.0, 0.0, 0.5]
    alignment_checks = [
        item for item in result["verification_recommended"] if item["tool_name"] == "scene_measure_alignment"
    ]
    assert alignment_checks
    assert alignment_checks[0]["arguments_hint"]["axes"] == ["X", "Y"]


def test_macro_relative_layout_rejects_negative_gap():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    try:
        handler.relative_layout(
            moving_object="Leg",
            reference_object="TableTop",
            contact_axis="Z",
            gap=-0.01,
        )
    except ValueError as exc:
        assert "gap must be >= 0" in str(exc)
    else:
        raise AssertionError("Expected negative gap to raise")
