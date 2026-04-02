from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler


class FakeSceneTool:
    def __init__(self):
        self.inspect_payload = {
            "Head": {"scale": [1.0, 1.0, 1.0]},
            "Body": {"scale": [1.0, 1.0, 1.0]},
        }
        self.ratios = {"before": 0.6, "after": 0.4}
        self.calls = 0

    def inspect_object(self, object_name):
        return self.inspect_payload[object_name]

    def assert_proportion(
        self,
        object_name,
        axis_a,
        expected_ratio,
        axis_b=None,
        reference_object=None,
        reference_axis=None,
        tolerance=0.01,
        world_space=True,
    ):
        ratio = self.ratios["before"] if self.calls == 0 else self.ratios["after"]
        self.calls += 1
        return {
            "assertion": "scene_assert_proportion",
            "passed": abs(ratio - expected_ratio) <= tolerance,
            "subject": object_name,
            "target": reference_object,
            "expected": {
                "ratio": expected_ratio,
                "axis_a": axis_a,
                "reference_object": reference_object,
                "reference_axis": reference_axis,
            },
            "actual": {"ratio": ratio, "mode": "cross_object"},
            "delta": {"ratio_delta": round(ratio - expected_ratio, 6)},
            "tolerance": tolerance,
            "units": "ratio",
            "details": {"world_space": world_space},
        }

    def measure_dimensions(self, object_name, world_space=True):
        return {"object_name": object_name, "dimensions": [1.0, 1.0, 1.0], "volume": 1.0, "units": "blender_units"}


class FakeModelingTool:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def transform_object(self, name, location=None, rotation=None, scale=None):
        self.calls.append(
            ("transform_object", {"name": name, "location": location, "rotation": rotation, "scale": scale})
        )
        return f"Transformed object '{name}'"


def test_macro_adjust_relative_proportion_scales_primary_toward_target_ratio():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    result = handler.adjust_relative_proportion(
        primary_object="Head",
        reference_object="Body",
        expected_ratio=0.4,
        primary_axis="X",
        reference_axis="X",
        scale_target="primary",
        max_scale_delta=0.5,
    )

    assert result["status"] == "success"
    assert result["macro_name"] == "macro_adjust_relative_proportion"
    assert modeling.calls[0][1]["name"] == "Head"
    assert modeling.calls[0][1]["scale"] == pytest.approx([0.666667, 0.666667, 0.666667], abs=1e-6)
    assert result["actions_taken"][1]["action"] == "adjust_relative_proportion"
    assert result["actions_taken"][-1]["details"]["passed"] is True


def test_macro_adjust_relative_proportion_blocks_when_scale_delta_is_too_large():
    scene = FakeSceneTool()
    modeling = FakeModelingTool()
    handler = MacroToolHandler(scene, modeling)

    result = handler.adjust_relative_proportion(
        primary_object="Head",
        reference_object="Body",
        expected_ratio=0.2,
        max_scale_delta=0.1,
    )

    assert result["status"] == "blocked"
    assert modeling.calls == []
    assert "exceeds max_scale_delta" in (result["error"] or "")
