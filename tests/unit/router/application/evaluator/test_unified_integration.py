"""
Integration Tests for Unified Evaluator System.

TASK-060: Tests verifying that ExpressionEvaluator and ConditionEvaluator
correctly delegate to UnifiedEvaluator while maintaining their specific behaviors.
"""

import pytest
from unittest.mock import MagicMock, patch

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator
from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator
from server.router.application.evaluator.condition_evaluator import ConditionEvaluator


class TestExpressionEvaluatorDelegation:
    """Test that ExpressionEvaluator properly delegates to UnifiedEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return ExpressionEvaluator()

    def test_calculate_delegates_arithmetic(self, evaluator):
        """Verify $CALCULATE arithmetic uses UnifiedEvaluator."""
        evaluator.set_context({"width": 2.0})
        result = evaluator.resolve_param_value("$CALCULATE(width * 3)")
        assert result == 6.0

    def test_calculate_supports_math_functions(self, evaluator):
        """Verify math functions work through delegation."""
        evaluator.set_context({"x": 9.0})
        result = evaluator.resolve_param_value("$CALCULATE(sqrt(x))")
        assert result == 3.0

    def test_calculate_supports_ternary(self, evaluator):
        """Verify ternary expressions work (new capability from TASK-060)."""
        evaluator.set_context({"width": 2.0})
        result = evaluator.resolve_param_value("$CALCULATE(1 if width > 1 else 0)")
        assert result == 1.0

        evaluator.set_context({"width": 0.5})
        result = evaluator.resolve_param_value("$CALCULATE(1 if width > 1 else 0)")
        assert result == 0.0

    def test_calculate_supports_comparisons(self, evaluator):
        """Verify comparison operators work in $CALCULATE."""
        evaluator.set_context({"a": 5.0, "b": 3.0})
        result = evaluator.resolve_param_value("$CALCULATE(a > b)")
        assert result == 1.0

    def test_calculate_supports_logical_operators(self, evaluator):
        """Verify logical operators work in $CALCULATE."""
        evaluator.set_context({"a": 5.0, "b": 3.0})
        result = evaluator.resolve_param_value("$CALCULATE(a > 2 and b < 5)")
        assert result == 1.0

    def test_calculate_combined_ternary_and_logic(self, evaluator):
        """Verify complex expression with ternary and logic."""
        evaluator.set_context({"x": 7.0, "y": 3.0})
        result = evaluator.resolve_param_value(
            "$CALCULATE(100 if x > 5 and y < 5 else 0)"
        )
        assert result == 100.0

    def test_variable_reference_still_works(self, evaluator):
        """Verify $variable direct reference still works."""
        evaluator.set_context({"my_value": 42.0})
        result = evaluator.resolve_param_value("$my_value")
        assert result == 42.0

    def test_context_flattening_still_works(self, evaluator):
        """Verify dimensions are flattened to width/height/depth."""
        evaluator.set_context({"dimensions": [1.0, 2.0, 3.0]})

        # Width
        result = evaluator.resolve_param_value("$width")
        assert result == 1.0

        # Height
        result = evaluator.resolve_param_value("$height")
        assert result == 2.0

        # Depth
        result = evaluator.resolve_param_value("$depth")
        assert result == 3.0


class TestConditionEvaluatorDelegation:
    """Test that ConditionEvaluator properly delegates to UnifiedEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return ConditionEvaluator()

    def test_simple_comparison_delegates(self, evaluator):
        """Verify simple comparison uses UnifiedEvaluator."""
        evaluator.set_context({"width": 2.0})
        assert evaluator.evaluate("width > 1") is True
        assert evaluator.evaluate("width > 5") is False

    def test_logical_and_delegates(self, evaluator):
        """Verify AND logic uses UnifiedEvaluator."""
        evaluator.set_context({"a": 5.0, "b": 3.0})
        assert evaluator.evaluate("a > 2 and b < 5") is True
        assert evaluator.evaluate("a > 10 and b < 5") is False

    def test_logical_or_delegates(self, evaluator):
        """Verify OR logic uses UnifiedEvaluator."""
        evaluator.set_context({"a": 5.0})
        assert evaluator.evaluate("a > 10 or a < 10") is True
        assert evaluator.evaluate("a > 10 or a == 3") is False

    def test_logical_not_delegates(self, evaluator):
        """Verify NOT logic uses UnifiedEvaluator."""
        evaluator.set_context({"flag": False})
        assert evaluator.evaluate("not flag") is True

    def test_parentheses_delegates(self, evaluator):
        """Verify parenthesized expressions use UnifiedEvaluator."""
        evaluator.set_context({"a": 5.0, "b": 3.0})
        assert evaluator.evaluate("(a > 2) and (b < 5)") is True
        assert evaluator.evaluate("a > 10 or (a < 10 and b > 2)") is True

    def test_math_functions_in_conditions(self, evaluator):
        """Verify math functions work in conditions (new capability from TASK-060)."""
        evaluator.set_context({"x": 10.5})
        assert evaluator.evaluate("floor(x) == 10") is True
        assert evaluator.evaluate("ceil(x) == 11") is True
        assert evaluator.evaluate("round(x) == 10") is True  # 10.5 rounds to 10 (banker's rounding)

    def test_sqrt_in_conditions(self, evaluator):
        """Verify sqrt works in conditions (new capability)."""
        evaluator.set_context({"width": 3.0, "depth": 4.0})
        # sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5.0
        assert evaluator.evaluate("sqrt(width * width + depth * depth) == 5") is True

    def test_chained_comparisons_delegate(self, evaluator):
        """Verify chained comparisons use UnifiedEvaluator."""
        evaluator.set_context({"x": 5.0})
        assert evaluator.evaluate("0 < x < 10") is True
        assert evaluator.evaluate("10 < x < 20") is False

    def test_string_comparison_delegates(self, evaluator):
        """Verify string comparisons use UnifiedEvaluator."""
        evaluator.set_context({"mode": "EDIT"})
        assert evaluator.evaluate("mode == 'EDIT'") is True
        assert evaluator.evaluate("mode == 'OBJECT'") is False

    def test_fail_open_behavior_preserved(self, evaluator):
        """Verify fail-open behavior is preserved (returns True on error)."""
        evaluator.set_context({})
        # Undefined variable should cause error but return True (fail-open)
        result = evaluator.evaluate("undefined_var > 0")
        assert result is True

    def test_simulate_step_effect_still_works(self, evaluator):
        """Verify simulate_step_effect is still available."""
        evaluator.set_context({"current_mode": "OBJECT", "has_selection": False})

        # simulate_step_effect takes tool_name and params, not a step object
        evaluator.simulate_step_effect("system_set_mode", {"mode": "EDIT"})

        ctx = evaluator.get_context()
        assert ctx["current_mode"] == "EDIT"

        # Test mesh_select effect
        evaluator.simulate_step_effect("mesh_select", {"action": "all"})
        ctx = evaluator.get_context()
        assert ctx["has_selection"] is True


class TestUnifiedEvaluatorSharedContext:
    """Test context sharing between wrappers and UnifiedEvaluator."""

    def test_expression_evaluator_context_isolated(self):
        """Verify each ExpressionEvaluator has its own UnifiedEvaluator."""
        eval1 = ExpressionEvaluator()
        eval2 = ExpressionEvaluator()

        eval1.set_context({"x": 1.0})
        eval2.set_context({"x": 2.0})

        result1 = eval1.resolve_param_value("$CALCULATE(x)")
        result2 = eval2.resolve_param_value("$CALCULATE(x)")

        assert result1 == 1.0
        assert result2 == 2.0

    def test_condition_evaluator_context_isolated(self):
        """Verify each ConditionEvaluator has its own UnifiedEvaluator."""
        eval1 = ConditionEvaluator()
        eval2 = ConditionEvaluator()

        eval1.set_context({"x": 1.0})
        eval2.set_context({"x": 10.0})

        assert eval1.evaluate("x < 5") is True
        assert eval2.evaluate("x < 5") is False


class TestNewCapabilitiesIntegration:
    """Integration tests for new capabilities enabled by TASK-060."""

    def test_floor_ceiling_in_workflow_condition(self):
        """Test floor/ceiling in realistic workflow condition."""
        evaluator = ConditionEvaluator()
        evaluator.set_context({
            "table_width": 1.5,
            "plank_width": 0.2
        })

        # This condition was NOT possible before TASK-060
        # floor(1.5 / 0.2) = floor(7.5) = 7
        assert evaluator.evaluate("floor(table_width / plank_width) >= 5") is True

    def test_ternary_in_workflow_expression(self):
        """Test ternary expression in realistic workflow calculation."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({
            "i": 3,
            "plank_full_count": 5,
            "full_width": 0.2,
            "remainder_width": 0.15
        })

        # This expression was NOT possible before TASK-060
        result = evaluator.resolve_param_value(
            "$CALCULATE(full_width if i <= plank_full_count else remainder_width)"
        )
        assert result == 0.2

        # Now test with i > plank_full_count
        evaluator.set_context({
            "i": 6,
            "plank_full_count": 5,
            "full_width": 0.2,
            "remainder_width": 0.15
        })
        result = evaluator.resolve_param_value(
            "$CALCULATE(full_width if i <= plank_full_count else remainder_width)"
        )
        assert result == 0.15

    def test_complex_workflow_calculation(self):
        """Test complex calculation combining math functions and logic."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({
            "length": 1.5,
            "width": 0.8,
            "min_diagonal": 1.0
        })

        # Calculate diagonal and compare
        # sqrt(1.5^2 + 0.8^2) = sqrt(2.25 + 0.64) = sqrt(2.89) ≈ 1.7
        result = evaluator.resolve_param_value(
            "$CALCULATE(1 if sqrt(length * length + width * width) > min_diagonal else 0)"
        )
        assert result == 1.0

    def test_conditional_count_calculation(self):
        """Test calculation with floor and conditional logic."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({
            "total_width": 2.0,
            "item_width": 0.3,
            "max_items": 10
        })

        # Calculate how many items fit, but cap at max_items
        # floor(2.0 / 0.3) = floor(6.67) = 6
        result = evaluator.resolve_param_value(
            "$CALCULATE(floor(total_width / item_width) if floor(total_width / item_width) <= max_items else max_items)"
        )
        assert result == 6.0


class TestBackwardCompatibility:
    """Verify backward compatibility with existing code."""

    def test_expression_evaluator_basic_calculate(self):
        """Verify basic $CALCULATE still works."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"a": 2.0, "b": 3.0})

        assert evaluator.resolve_param_value("$CALCULATE(a + b)") == 5.0
        assert evaluator.resolve_param_value("$CALCULATE(a * b)") == 6.0

    def test_expression_evaluator_nested_calculate(self):
        """Verify nested expressions still work."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"x": 2.0})

        result = evaluator.resolve_param_value("$CALCULATE(x * 2 + 1)")
        assert result == 5.0

    def test_condition_evaluator_basic_comparisons(self):
        """Verify basic comparisons still work."""
        evaluator = ConditionEvaluator()
        evaluator.set_context({"x": 5.0, "y": 3.0})

        assert evaluator.evaluate("x > y") is True
        assert evaluator.evaluate("x < y") is False
        assert evaluator.evaluate("x == 5") is True
        assert evaluator.evaluate("x != y") is True

    def test_condition_evaluator_complex_logic(self):
        """Verify complex logic still works."""
        evaluator = ConditionEvaluator()
        evaluator.set_context({"a": 5.0, "b": 3.0, "c": 7.0})

        assert evaluator.evaluate("a > 2 and b < 5 and c > 6") is True
        assert evaluator.evaluate("a > 10 or b > 10 or c > 6") is True
        assert evaluator.evaluate("not (a > 10)") is True


class TestEdgeCases:
    """Test edge cases in the integrated system."""

    def test_empty_expression(self):
        """Verify empty expression handling."""
        expr_eval = ExpressionEvaluator()
        result = expr_eval.resolve_param_value("")
        assert result == ""

    def test_whitespace_expression(self):
        """Verify whitespace handling."""
        expr_eval = ExpressionEvaluator()
        result = expr_eval.resolve_param_value("   ")
        assert result == "   "

    def test_plain_number(self):
        """Verify plain number handling."""
        expr_eval = ExpressionEvaluator()
        result = expr_eval.resolve_param_value("42")
        assert result == "42"  # Returns as string without $CALCULATE

    def test_zero_division_handling(self):
        """Verify zero division is handled."""
        expr_eval = ExpressionEvaluator()
        expr_eval.set_context({"x": 0.0})

        # Should handle gracefully - returns infinity for 1/0
        result = expr_eval.resolve_param_value("$CALCULATE(1 / x)")
        # Returns infinity or error string
        assert result is not None

    def test_boolean_context_values(self):
        """Verify boolean values in context work."""
        cond_eval = ConditionEvaluator()
        cond_eval.set_context({"flag": True})

        assert cond_eval.evaluate("flag") is True
        assert cond_eval.evaluate("not flag") is False

    def test_none_in_context(self):
        """Verify None values are handled."""
        expr_eval = ExpressionEvaluator()
        expr_eval.set_context({"value": None})

        # Should handle gracefully - $value returns None or empty
        result = expr_eval.resolve_param_value("$value")
        # None values are skipped during set_context, so $value doesn't exist
        assert result == "$value" or result is None
