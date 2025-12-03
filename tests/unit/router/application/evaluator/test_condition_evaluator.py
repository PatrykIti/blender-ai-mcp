"""
Tests for Condition Evaluator.

TASK-041-10
"""

import pytest
from server.router.application.evaluator.condition_evaluator import ConditionEvaluator


class TestConditionEvaluatorInit:
    """Test evaluator initialization."""

    def test_init_empty_context(self):
        evaluator = ConditionEvaluator()
        assert evaluator.get_context() == {}

    def test_set_context(self):
        evaluator = ConditionEvaluator()
        evaluator.set_context({"current_mode": "OBJECT", "has_selection": True})

        context = evaluator.get_context()
        assert context["current_mode"] == "OBJECT"
        assert context["has_selection"] is True

    def test_update_context(self):
        evaluator = ConditionEvaluator()
        evaluator.set_context({"current_mode": "OBJECT"})
        evaluator.update_context({"has_selection": True})

        context = evaluator.get_context()
        assert context["current_mode"] == "OBJECT"
        assert context["has_selection"] is True

    def test_set_context_copies_dict(self):
        """Ensure context is copied, not referenced."""
        evaluator = ConditionEvaluator()
        original = {"current_mode": "OBJECT"}
        evaluator.set_context(original)

        original["current_mode"] = "EDIT"
        assert evaluator.get_context()["current_mode"] == "OBJECT"


class TestEqualityComparisons:
    """Test equality comparison operators."""

    @pytest.fixture
    def evaluator(self):
        e = ConditionEvaluator()
        e.set_context({
            "current_mode": "OBJECT",
            "active_object": "Cube",
            "object_count": 5,
        })
        return e

    def test_equal_string(self, evaluator):
        assert evaluator.evaluate("current_mode == 'OBJECT'") is True
        assert evaluator.evaluate("current_mode == 'EDIT'") is False

    def test_equal_string_double_quotes(self, evaluator):
        assert evaluator.evaluate('current_mode == "OBJECT"') is True
        assert evaluator.evaluate('current_mode == "EDIT"') is False

    def test_not_equal_string(self, evaluator):
        assert evaluator.evaluate("current_mode != 'EDIT'") is True
        assert evaluator.evaluate("current_mode != 'OBJECT'") is False

    def test_equal_number(self, evaluator):
        assert evaluator.evaluate("object_count == 5") is True
        assert evaluator.evaluate("object_count == 3") is False

    def test_not_equal_number(self, evaluator):
        assert evaluator.evaluate("object_count != 3") is True
        assert evaluator.evaluate("object_count != 5") is False


class TestNumericComparisons:
    """Test numeric comparison operators."""

    @pytest.fixture
    def evaluator(self):
        e = ConditionEvaluator()
        e.set_context({
            "object_count": 5,
            "selected_verts": 10,
            "selected_faces": 0,
        })
        return e

    def test_greater_than(self, evaluator):
        assert evaluator.evaluate("object_count > 3") is True
        assert evaluator.evaluate("object_count > 5") is False
        assert evaluator.evaluate("object_count > 10") is False

    def test_less_than(self, evaluator):
        assert evaluator.evaluate("object_count < 10") is True
        assert evaluator.evaluate("object_count < 5") is False
        assert evaluator.evaluate("object_count < 3") is False

    def test_greater_than_or_equal(self, evaluator):
        assert evaluator.evaluate("object_count >= 5") is True
        assert evaluator.evaluate("object_count >= 3") is True
        assert evaluator.evaluate("object_count >= 10") is False

    def test_less_than_or_equal(self, evaluator):
        assert evaluator.evaluate("object_count <= 5") is True
        assert evaluator.evaluate("object_count <= 10") is True
        assert evaluator.evaluate("object_count <= 3") is False

    def test_zero_comparison(self, evaluator):
        assert evaluator.evaluate("selected_faces == 0") is True
        assert evaluator.evaluate("selected_faces > 0") is False
        assert evaluator.evaluate("selected_verts > 0") is True


class TestBooleanVariables:
    """Test boolean variable evaluation."""

    @pytest.fixture
    def evaluator(self):
        e = ConditionEvaluator()
        e.set_context({
            "has_selection": True,
            "is_active": False,
        })
        return e

    def test_true_variable(self, evaluator):
        assert evaluator.evaluate("has_selection") is True

    def test_false_variable(self, evaluator):
        assert evaluator.evaluate("is_active") is False

    def test_not_true_variable(self, evaluator):
        assert evaluator.evaluate("not has_selection") is False

    def test_not_false_variable(self, evaluator):
        assert evaluator.evaluate("not is_active") is True


class TestLogicalOperators:
    """Test logical operators (and, or, not)."""

    @pytest.fixture
    def evaluator(self):
        e = ConditionEvaluator()
        e.set_context({
            "current_mode": "EDIT",
            "has_selection": True,
            "object_count": 5,
        })
        return e

    def test_and_both_true(self, evaluator):
        result = evaluator.evaluate("current_mode == 'EDIT' and has_selection")
        assert result is True

    def test_and_first_false(self, evaluator):
        result = evaluator.evaluate("current_mode == 'OBJECT' and has_selection")
        assert result is False

    def test_and_second_false(self, evaluator):
        result = evaluator.evaluate("current_mode == 'EDIT' and object_count > 10")
        assert result is False

    def test_or_both_true(self, evaluator):
        result = evaluator.evaluate("current_mode == 'EDIT' or has_selection")
        assert result is True

    def test_or_first_true(self, evaluator):
        result = evaluator.evaluate("current_mode == 'EDIT' or object_count > 100")
        assert result is True

    def test_or_second_true(self, evaluator):
        result = evaluator.evaluate("current_mode == 'OBJECT' or has_selection")
        assert result is True

    def test_or_both_false(self, evaluator):
        result = evaluator.evaluate("current_mode == 'OBJECT' or object_count > 100")
        assert result is False

    def test_not_with_comparison(self, evaluator):
        result = evaluator.evaluate("not current_mode == 'OBJECT'")
        assert result is True

    def test_complex_expression(self, evaluator):
        # Note: and has higher precedence than or in most languages,
        # but our simple parser evaluates left-to-right
        result = evaluator.evaluate("has_selection and object_count > 0")
        assert result is True


class TestLiteralValues:
    """Test literal value parsing."""

    @pytest.fixture
    def evaluator(self):
        return ConditionEvaluator()

    def test_true_literal(self, evaluator):
        assert evaluator.evaluate("true") is True
        assert evaluator.evaluate("True") is True
        assert evaluator.evaluate("TRUE") is True

    def test_false_literal(self, evaluator):
        assert evaluator.evaluate("false") is False
        assert evaluator.evaluate("False") is False
        assert evaluator.evaluate("FALSE") is False


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def evaluator(self):
        e = ConditionEvaluator()
        e.set_context({"current_mode": "OBJECT"})
        return e

    def test_empty_condition(self, evaluator):
        # Empty condition should return True (execute step)
        assert evaluator.evaluate("") is True
        assert evaluator.evaluate("   ") is True

    def test_none_condition(self, evaluator):
        assert evaluator.evaluate(None) is True

    def test_unknown_variable(self, evaluator):
        # Unknown variable should fail-open (return True)
        assert evaluator.evaluate("unknown_var") is True

    def test_whitespace_handling(self, evaluator):
        assert evaluator.evaluate("  current_mode == 'OBJECT'  ") is True
        assert evaluator.evaluate("current_mode  ==  'OBJECT'") is True

    def test_malformed_condition_fails_open(self, evaluator):
        # Malformed conditions without valid comparison should fail-open
        # Note: "== invalid" gets parsed as "" == "invalid" which is False,
        # but truly unparseable conditions fail-open
        assert evaluator.evaluate("something without operator") is True
        assert evaluator.evaluate("@#$%^&") is True


class TestSimulateStepEffect:
    """Test context simulation for workflow execution."""

    @pytest.fixture
    def evaluator(self):
        e = ConditionEvaluator()
        e.set_context({
            "current_mode": "OBJECT",
            "has_selection": False,
            "object_count": 1,
        })
        return e

    def test_simulate_mode_change(self, evaluator):
        evaluator.simulate_step_effect("system_set_mode", {"mode": "EDIT"})
        assert evaluator.get_context()["current_mode"] == "EDIT"

    def test_simulate_scene_set_mode(self, evaluator):
        evaluator.simulate_step_effect("scene_set_mode", {"mode": "SCULPT"})
        assert evaluator.get_context()["current_mode"] == "SCULPT"

    def test_simulate_select_all(self, evaluator):
        evaluator.simulate_step_effect("mesh_select", {"action": "all"})
        assert evaluator.get_context()["has_selection"] is True

    def test_simulate_deselect(self, evaluator):
        evaluator.set_context({"has_selection": True})
        evaluator.simulate_step_effect("mesh_select", {"action": "none"})
        assert evaluator.get_context()["has_selection"] is False

    def test_simulate_targeted_select(self, evaluator):
        evaluator.simulate_step_effect("mesh_select_targeted", {"indices": [0, 1, 2]})
        assert evaluator.get_context()["has_selection"] is True

    def test_simulate_create_primitive(self, evaluator):
        initial_count = evaluator.get_context()["object_count"]
        evaluator.simulate_step_effect("modeling_create_primitive", {"type": "CUBE"})
        assert evaluator.get_context()["object_count"] == initial_count + 1

    def test_simulate_delete_object(self, evaluator):
        evaluator.set_context({"object_count": 3})
        evaluator.simulate_step_effect("scene_delete_object", {"name": "Cube"})
        assert evaluator.get_context()["object_count"] == 2

    def test_simulate_delete_at_zero(self, evaluator):
        evaluator.set_context({"object_count": 0})
        evaluator.simulate_step_effect("scene_delete_object", {"name": "Cube"})
        assert evaluator.get_context()["object_count"] == 0  # Can't go negative


class TestRealWorldConditions:
    """Test real-world workflow condition examples."""

    def test_mode_switch_condition(self):
        """Test: only switch to EDIT if not already in EDIT."""
        evaluator = ConditionEvaluator()

        # Already in EDIT mode - should NOT execute mode switch
        evaluator.set_context({"current_mode": "EDIT"})
        assert evaluator.evaluate("current_mode != 'EDIT'") is False

        # In OBJECT mode - SHOULD execute mode switch
        evaluator.set_context({"current_mode": "OBJECT"})
        assert evaluator.evaluate("current_mode != 'EDIT'") is True

    def test_selection_condition(self):
        """Test: only select all if nothing selected."""
        evaluator = ConditionEvaluator()

        # Has selection - should NOT select all
        evaluator.set_context({"has_selection": True})
        assert evaluator.evaluate("not has_selection") is False

        # No selection - SHOULD select all
        evaluator.set_context({"has_selection": False})
        assert evaluator.evaluate("not has_selection") is True

    def test_object_exists_condition(self):
        """Test: only delete if objects exist."""
        evaluator = ConditionEvaluator()

        # Objects exist - SHOULD be able to delete
        evaluator.set_context({"object_count": 5})
        assert evaluator.evaluate("object_count > 0") is True

        # No objects - should NOT delete
        evaluator.set_context({"object_count": 0})
        assert evaluator.evaluate("object_count > 0") is False

    def test_combined_condition(self):
        """Test: edit mode AND has selection."""
        evaluator = ConditionEvaluator()

        # Both true
        evaluator.set_context({"current_mode": "EDIT", "has_selection": True})
        assert evaluator.evaluate("current_mode == 'EDIT' and has_selection") is True

        # Mode wrong
        evaluator.set_context({"current_mode": "OBJECT", "has_selection": True})
        assert evaluator.evaluate("current_mode == 'EDIT' and has_selection") is False

        # No selection
        evaluator.set_context({"current_mode": "EDIT", "has_selection": False})
        assert evaluator.evaluate("current_mode == 'EDIT' and has_selection") is False

    def test_workflow_simulation(self):
        """Test: simulate a workflow with conditional steps."""
        evaluator = ConditionEvaluator()
        evaluator.set_context({
            "current_mode": "OBJECT",
            "has_selection": False,
        })

        # Step 1: Switch to EDIT mode (condition: not in EDIT)
        step1_should_run = evaluator.evaluate("current_mode != 'EDIT'")
        assert step1_should_run is True
        evaluator.simulate_step_effect("system_set_mode", {"mode": "EDIT"})

        # Step 2: Select all (condition: no selection)
        step2_should_run = evaluator.evaluate("not has_selection")
        assert step2_should_run is True
        evaluator.simulate_step_effect("mesh_select", {"action": "all"})

        # Step 3: Another mode check (should NOT run - already in EDIT)
        step3_should_run = evaluator.evaluate("current_mode != 'EDIT'")
        assert step3_should_run is False

        # Step 4: Another selection check (should NOT run - already selected)
        step4_should_run = evaluator.evaluate("not has_selection")
        assert step4_should_run is False
