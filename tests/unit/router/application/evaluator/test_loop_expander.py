"""
Unit tests for LoopExpander.

TASK-058: Loop System & String Interpolation for Workflows.
"""

import pytest

from server.router.application.evaluator.loop_expander import LoopExpander
from server.router.application.workflows.base import WorkflowStep


class TestLoopExpanderInterpolation:
    def test_interpolation_without_loop_and_escaping(self):
        expander = LoopExpander()

        step = WorkflowStep(
            tool="test_tool",
            params={
                "name": "Obj_{x}_{{y}}",
                "nested": {"label": "L_{x}"},
            },
            description="Desc {x}",
            condition="{x} > 1",
            id="id_{x}",
            depends_on=["dep_{x}"],
        )
        setattr(step, "custom_attr", "A_{x}_{{z}}")

        out = expander.expand([step], {"x": 5})

        assert len(out) == 1
        expanded = out[0]
        assert expanded.loop is None

        assert expanded.params["name"] == "Obj_5_{y}"
        assert expanded.params["nested"]["label"] == "L_5"
        assert expanded.description == "Desc 5"
        assert expanded.condition == "5 > 1"
        assert expanded.id == "id_5"
        assert expanded.depends_on == ["dep_5"]
        assert getattr(expanded, "custom_attr") == "A_5_{z}"

    def test_interpolation_strict_unknown_raises(self):
        expander = LoopExpander()
        step = WorkflowStep(tool="test_tool", params={"name": "Obj_{missing}"})

        with pytest.raises(ValueError, match="Unknown placeholder"):
            expander.expand([step], {})


class TestLoopExpanderLoops:
    def test_values_loop_expands_and_clears_loop(self):
        expander = LoopExpander()
        step = WorkflowStep(
            tool="test_tool",
            params={"name": "Side_{side}"},
            loop={"variable": "side", "values": ["L", "R"]},
        )

        out = expander.expand([step], {})

        assert [s.params["name"] for s in out] == ["Side_L", "Side_R"]
        assert all(s.loop is None for s in out)

    def test_range_loop_inclusive_with_expression(self):
        expander = LoopExpander()
        step = WorkflowStep(
            tool="test_tool",
            params={"value": "{i}"},
            loop={"variable": "i", "range": "1..(count + 1)"},
        )

        out = expander.expand([step], {"count": 2})

        assert [s.params["value"] for s in out] == ["1", "2", "3"]
        assert all(s.loop is None for s in out)

    def test_nested_loops_cross_product_order(self):
        expander = LoopExpander()
        step = WorkflowStep(
            tool="test_tool",
            params={"name": "B_{row}_{col}"},
            loop={
                "variables": ["row", "col"],
                "ranges": ["0..(rows - 1)", "0..(cols - 1)"],
            },
        )

        out = expander.expand([step], {"rows": 2, "cols": 3})

        assert [s.params["name"] for s in out] == [
            "B_0_0",
            "B_0_1",
            "B_0_2",
            "B_1_0",
            "B_1_1",
            "B_1_2",
        ]
        assert all(s.loop is None for s in out)

    def test_group_interleaves_consecutive_steps(self):
        expander = LoopExpander()
        steps = [
            WorkflowStep(
                tool="test_tool",
                params={"name": "A_{i}"},
                loop={"group": "g", "variable": "i", "range": "1..n"},
            ),
            WorkflowStep(
                tool="test_tool",
                params={"name": "B_{i}"},
                loop={"group": "g", "variable": "i", "range": "1..n"},
            ),
        ]

        out = expander.expand(steps, {"n": 3})

        assert [s.params["name"] for s in out] == ["A_1", "B_1", "A_2", "B_2", "A_3", "B_3"]
        assert all(s.loop is None for s in out)

    def test_max_expanded_steps_limit(self):
        expander = LoopExpander(max_expanded_steps=3)
        step = WorkflowStep(
            tool="test_tool",
            params={},
            loop={"variable": "i", "range": "1..10"},
        )

        with pytest.raises(ValueError, match="limit=3"):
            expander.expand([step], {})

