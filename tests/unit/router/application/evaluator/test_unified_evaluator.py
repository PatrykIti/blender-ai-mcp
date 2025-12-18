"""
Tests for UnifiedEvaluator.

TASK-060: Tests for AST-based unified evaluator.
"""

import math
import pytest
from typing import Any

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator
from server.router.domain.entities.parameter import ParameterSchema


class TestUnifiedEvaluatorInit:
    """Test initialization and context management."""

    def test_init_empty_context(self):
        """Test that evaluator initializes with empty context."""
        evaluator = UnifiedEvaluator()
        assert evaluator.get_context() == {}

    def test_set_context(self):
        """Test setting context with various types."""
        evaluator = UnifiedEvaluator()
        evaluator.set_context({
            "width": 2.0,
            "height": 4,
            "has_selection": True,
            "mode": "EDIT"
        })
        ctx = evaluator.get_context()
        assert ctx["width"] == 2.0
        assert ctx["height"] == 4.0  # int converted to float
        assert ctx["has_selection"] == True  # Original type preserved
        assert ctx["mode"] == "EDIT"

    def test_set_context_bool_handling(self):
        """Test that bool values are preserved."""
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"flag": True, "disabled": False})
        ctx = evaluator.get_context()
        assert ctx["flag"] is True
        assert ctx["disabled"] is False

    def test_update_context(self):
        """Test updating existing context."""
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"a": 1.0})
        evaluator.update_context({"b": 2.0, "a": 3.0})
        ctx = evaluator.get_context()
        assert ctx["a"] == 3.0
        assert ctx["b"] == 2.0

    def test_get_variable(self):
        """Test getting individual variables."""
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"x": 5.0, "name": "test"})
        assert evaluator.get_variable("x") == 5.0
        assert evaluator.get_variable("name") == "test"
        assert evaluator.get_variable("unknown") is None


class TestArithmeticOperations:
    """Test arithmetic operators."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"x": 10.0, "y": 3.0})
        return e

    def test_addition(self, evaluator):
        assert evaluator.evaluate("2 + 3") == 5.0

    def test_subtraction(self, evaluator):
        assert evaluator.evaluate("10 - 4") == 6.0

    def test_multiplication(self, evaluator):
        assert evaluator.evaluate("3 * 4") == 12.0

    def test_division(self, evaluator):
        assert evaluator.evaluate("15 / 3") == 5.0

    def test_floor_division(self, evaluator):
        assert evaluator.evaluate("17 // 5") == 3.0

    def test_modulo(self, evaluator):
        assert evaluator.evaluate("17 % 5") == 2.0

    def test_power(self, evaluator):
        assert evaluator.evaluate("2 ** 3") == 8.0

    def test_unary_minus(self, evaluator):
        assert evaluator.evaluate("-5") == -5.0

    def test_unary_plus(self, evaluator):
        assert evaluator.evaluate("+5") == 5.0

    def test_with_variables(self, evaluator):
        assert evaluator.evaluate("x + y") == 13.0
        assert evaluator.evaluate("x * y") == 30.0

    def test_complex_expression(self, evaluator):
        assert evaluator.evaluate("(x + y) * 2 - 1") == 25.0


class TestMathFunctions:
    """Test all 22 math functions."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    # Basic functions
    def test_abs(self, evaluator):
        assert evaluator.evaluate("abs(-5)") == 5.0

    def test_min(self, evaluator):
        assert evaluator.evaluate("min(3, 1, 4)") == 1.0

    def test_max(self, evaluator):
        assert evaluator.evaluate("max(3, 1, 4)") == 4.0

    def test_round(self, evaluator):
        assert evaluator.evaluate("round(3.7)") == 4.0
        # round with ndigits - now properly converts second arg to int
        assert evaluator.evaluate("round(3.14159, 2)") == 3.14

    def test_floor(self, evaluator):
        assert evaluator.evaluate("floor(3.7)") == 3.0

    def test_ceil(self, evaluator):
        assert evaluator.evaluate("ceil(3.2)") == 4.0

    def test_sqrt(self, evaluator):
        assert evaluator.evaluate("sqrt(16)") == 4.0

    def test_trunc(self, evaluator):
        assert evaluator.evaluate("trunc(3.9)") == 3.0
        assert evaluator.evaluate("trunc(-3.9)") == -3.0

    # Trigonometric functions
    def test_sin(self, evaluator):
        assert evaluator.evaluate("sin(0)") == 0.0
        assert abs(evaluator.evaluate("sin(1.5708)") - 1.0) < 0.001

    def test_cos(self, evaluator):
        assert evaluator.evaluate("cos(0)") == 1.0
        assert abs(evaluator.evaluate("cos(3.14159)") - (-1.0)) < 0.001

    def test_tan(self, evaluator):
        assert evaluator.evaluate("tan(0)") == 0.0

    def test_asin(self, evaluator):
        assert abs(evaluator.evaluate("asin(1)") - math.pi / 2) < 0.001

    def test_acos(self, evaluator):
        assert abs(evaluator.evaluate("acos(0)") - math.pi / 2) < 0.001

    def test_atan(self, evaluator):
        assert evaluator.evaluate("atan(0)") == 0.0

    def test_atan2(self, evaluator):
        assert abs(evaluator.evaluate("atan2(1, 1)") - math.pi / 4) < 0.001

    def test_degrees(self, evaluator):
        assert abs(evaluator.evaluate("degrees(3.14159)") - 180.0) < 0.01

    def test_radians(self, evaluator):
        assert abs(evaluator.evaluate("radians(180)") - math.pi) < 0.001

    # Logarithmic functions
    def test_log(self, evaluator):
        assert abs(evaluator.evaluate("log(2.71828)") - 1.0) < 0.001

    def test_log10(self, evaluator):
        assert evaluator.evaluate("log10(100)") == 2.0

    def test_exp(self, evaluator):
        assert abs(evaluator.evaluate("exp(1)") - math.e) < 0.001

    # Advanced functions
    def test_pow(self, evaluator):
        assert evaluator.evaluate("pow(2, 3)") == 8.0

    def test_hypot(self, evaluator):
        assert evaluator.evaluate("hypot(3, 4)") == 5.0


class TestComparisonOperators:
    """Test comparison operators."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"x": 5.0, "y": 10.0, "mode": "EDIT"})
        return e

    def test_equal(self, evaluator):
        assert evaluator.evaluate_as_bool("x == 5") is True
        assert evaluator.evaluate_as_bool("x == 6") is False

    def test_not_equal(self, evaluator):
        assert evaluator.evaluate_as_bool("x != 6") is True
        assert evaluator.evaluate_as_bool("x != 5") is False

    def test_less_than(self, evaluator):
        assert evaluator.evaluate_as_bool("x < 10") is True
        assert evaluator.evaluate_as_bool("x < 5") is False

    def test_less_equal(self, evaluator):
        assert evaluator.evaluate_as_bool("x <= 5") is True
        assert evaluator.evaluate_as_bool("x <= 4") is False

    def test_greater_than(self, evaluator):
        assert evaluator.evaluate_as_bool("y > 5") is True
        assert evaluator.evaluate_as_bool("y > 10") is False

    def test_greater_equal(self, evaluator):
        assert evaluator.evaluate_as_bool("y >= 10") is True
        assert evaluator.evaluate_as_bool("y >= 11") is False


class TestChainedComparisons:
    """Test chained comparisons (TASK-060 new capability)."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"x": 5.0})
        return e

    def test_chained_range(self, evaluator):
        """Test 0 < x < 10."""
        assert evaluator.evaluate_as_bool("0 < x < 10") is True
        assert evaluator.evaluate_as_bool("0 < x < 3") is False
        assert evaluator.evaluate_as_bool("6 < x < 10") is False

    def test_chained_inclusive(self, evaluator):
        """Test 0 <= x <= 10."""
        assert evaluator.evaluate_as_bool("0 <= x <= 10") is True
        assert evaluator.evaluate_as_bool("5 <= x <= 5") is True
        assert evaluator.evaluate_as_bool("6 <= x <= 10") is False

    def test_chained_mixed(self, evaluator):
        """Test 0 < x <= 5."""
        assert evaluator.evaluate_as_bool("0 < x <= 5") is True
        assert evaluator.evaluate_as_bool("0 <= x < 5") is False


class TestLogicalOperators:
    """Test logical operators with proper precedence."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"a": True, "b": False, "c": True})
        return e

    def test_and_true(self, evaluator):
        assert evaluator.evaluate_as_bool("a and c") is True

    def test_and_false(self, evaluator):
        assert evaluator.evaluate_as_bool("a and b") is False

    def test_or_true(self, evaluator):
        assert evaluator.evaluate_as_bool("a or b") is True

    def test_or_false(self, evaluator):
        evaluator.set_context({"a": False, "b": False})
        assert evaluator.evaluate_as_bool("a or b") is False

    def test_not(self, evaluator):
        assert evaluator.evaluate_as_bool("not b") is True
        assert evaluator.evaluate_as_bool("not a") is False

    def test_precedence_not_before_and(self, evaluator):
        """Test that not has higher precedence than and."""
        # not b should evaluate first, giving True, then True and True = True
        assert evaluator.evaluate_as_bool("a and not b") is True

    def test_precedence_and_before_or(self, evaluator):
        """Test that and has higher precedence than or."""
        # a and b = False, then False or c = True
        assert evaluator.evaluate_as_bool("a and b or c") is True

    def test_parentheses_override(self, evaluator):
        """Test that parentheses override precedence."""
        # Without parentheses: a and (b or c) = True and True = True
        # With parentheses: (a and b) or c = False or True = True
        assert evaluator.evaluate_as_bool("(a and b) or c") is True
        # a and (b or c) would still be True, but test the grouping
        evaluator.set_context({"a": False, "b": True, "c": False})
        assert evaluator.evaluate_as_bool("a and (b or c)") is False
        assert evaluator.evaluate_as_bool("(a and b) or c") is False


class TestTernaryExpressions:
    """Test ternary expressions (TASK-060 new capability)."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"x": 5.0, "flag": True})
        return e

    def test_true_branch(self, evaluator):
        assert evaluator.evaluate("10 if flag else 20") == 10.0

    def test_false_branch(self, evaluator):
        evaluator.set_context({"flag": False})
        assert evaluator.evaluate("10 if flag else 20") == 20.0

    def test_with_comparison(self, evaluator):
        assert evaluator.evaluate("1 if x > 3 else 0") == 1.0
        assert evaluator.evaluate("1 if x > 10 else 0") == 0.0

    def test_with_expressions(self, evaluator):
        """Test ternary with expressions in branches."""
        assert evaluator.evaluate("x * 2 if flag else x / 2") == 10.0
        evaluator.set_context({"x": 5.0, "flag": False})
        assert evaluator.evaluate("x * 2 if flag else x / 2") == 2.5

    def test_nested_ternary(self, evaluator):
        """Test nested ternary expression."""
        evaluator.set_context({"x": 2.0})
        # x < 0 ? -1 : (x == 0 ? 0 : 1)
        result = evaluator.evaluate("-1 if x < 0 else (0 if x == 0 else 1)")
        assert result == 1.0


class TestStringComparisons:
    """Test string comparisons for mode checks."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"mode": "EDIT", "name": "Cube"})
        return e

    def test_single_quotes(self, evaluator):
        assert evaluator.evaluate_as_bool("mode == 'EDIT'") is True
        assert evaluator.evaluate_as_bool("mode == 'OBJECT'") is False

    def test_double_quotes(self, evaluator):
        assert evaluator.evaluate_as_bool('mode == "EDIT"') is True
        assert evaluator.evaluate_as_bool('mode == "OBJECT"') is False

    def test_not_equal_string(self, evaluator):
        assert evaluator.evaluate_as_bool("mode != 'OBJECT'") is True
        assert evaluator.evaluate_as_bool("mode != 'EDIT'") is False

    def test_string_variable(self, evaluator):
        assert evaluator.evaluate_as_bool("name == 'Cube'") is True


class TestBooleanLiterals:
    """Test boolean literals."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_true_literal(self, evaluator):
        assert evaluator.evaluate_as_bool("True") is True

    def test_false_literal(self, evaluator):
        assert evaluator.evaluate_as_bool("False") is False

    def test_lowercase_true(self, evaluator):
        """Test lowercase true (TASK-060 compatibility)."""
        assert evaluator.evaluate_as_bool("true") is True

    def test_lowercase_false(self, evaluator):
        """Test lowercase false (TASK-060 compatibility)."""
        assert evaluator.evaluate_as_bool("false") is False

    def test_in_expression(self, evaluator):
        evaluator.set_context({"x": 5.0})
        assert evaluator.evaluate_as_bool("True and x > 0") is True
        assert evaluator.evaluate_as_bool("False or x > 0") is True


class TestComputedParameters:
    """Test computed parameter resolution."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_simple_computed(self, evaluator):
        """Test simple computed parameter."""
        schemas = {
            "width": ParameterSchema(name="width", type="float"),
            "half_width": ParameterSchema(
                name="half_width",
                type="float",
                computed="width / 2",
                depends_on=["width"]
            )
        }
        context = {"width": 10.0}
        result = evaluator.resolve_computed_parameters(schemas, context)
        assert result["width"] == 10.0
        assert result["half_width"] == 5.0

    def test_dependency_chain(self, evaluator):
        """Test computed parameters with dependencies."""
        schemas = {
            "x": ParameterSchema(name="x", type="float"),
            "y": ParameterSchema(
                name="y",
                type="float",
                computed="x * 2",
                depends_on=["x"]
            ),
            "z": ParameterSchema(
                name="z",
                type="float",
                computed="y + 1",
                depends_on=["y"]
            )
        }
        context = {"x": 5.0}
        result = evaluator.resolve_computed_parameters(schemas, context)
        assert result["x"] == 5.0
        assert result["y"] == 10.0
        assert result["z"] == 11.0

    def test_with_math_functions(self, evaluator):
        """Test computed parameters with math functions."""
        schemas = {
            "value": ParameterSchema(name="value", type="float"),
            "rounded": ParameterSchema(
                name="rounded",
                type="float",
                computed="floor(value)",
                depends_on=["value"]
            )
        }
        context = {"value": 3.7}
        result = evaluator.resolve_computed_parameters(schemas, context)
        assert result["rounded"] == 3.0

    def test_circular_dependency(self, evaluator):
        """Test circular dependency detection."""
        schemas = {
            "a": ParameterSchema(
                name="a",
                type="float",
                computed="b + 1",
                depends_on=["b"]
            ),
            "b": ParameterSchema(
                name="b",
                type="float",
                computed="a + 1",
                depends_on=["a"]
            )
        }
        with pytest.raises(ValueError, match="[Cc]ircular"):
            evaluator.resolve_computed_parameters(schemas, {})

    def test_no_computed(self, evaluator):
        """Test with no computed parameters."""
        schemas = {
            "x": ParameterSchema(name="x", type="float"),
            "y": ParameterSchema(name="y", type="float")
        }
        context = {"x": 1.0, "y": 2.0}
        result = evaluator.resolve_computed_parameters(schemas, context)
        assert result == {"x": 1.0, "y": 2.0}


class TestTopologicalSort:
    """Test topological sorting of dependency graph."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_linear_graph(self, evaluator):
        """Test simple linear dependency graph."""
        graph = {"a": [], "b": ["a"], "c": ["b"]}
        result = evaluator._topological_sort(graph)
        assert result.index("a") < result.index("b")
        assert result.index("b") < result.index("c")

    def test_parallel_branches(self, evaluator):
        """Test graph with parallel branches."""
        graph = {"root": [], "a": ["root"], "b": ["root"], "c": ["a", "b"]}
        result = evaluator._topological_sort(graph)
        assert result.index("root") < result.index("a")
        assert result.index("root") < result.index("b")
        assert result.index("a") < result.index("c")
        assert result.index("b") < result.index("c")

    def test_circular_dependency(self, evaluator):
        """Test circular dependency raises error."""
        graph = {"a": ["b"], "b": ["a"]}
        with pytest.raises(ValueError, match="[Cc]ircular"):
            evaluator._topological_sort(graph)

    def test_empty_graph(self, evaluator):
        """Test empty graph."""
        result = evaluator._topological_sort({})
        assert result == []


class TestErrorHandling:
    """Test error handling."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_empty_expression(self, evaluator):
        with pytest.raises(ValueError, match="[Ee]mpty"):
            evaluator.evaluate("")

    def test_whitespace_only(self, evaluator):
        with pytest.raises(ValueError, match="[Ee]mpty"):
            evaluator.evaluate("   ")

    def test_syntax_error(self, evaluator):
        with pytest.raises(ValueError, match="[Ss]yntax|[Ii]nvalid"):
            # Use actually invalid syntax
            evaluator.evaluate("2 +* 3")

    def test_unknown_variable(self, evaluator):
        with pytest.raises(ValueError, match="[Uu]nknown|[Nn]ot found"):
            evaluator.evaluate("unknown_var + 1")

    def test_unknown_function(self, evaluator):
        with pytest.raises(ValueError, match="[Uu]nknown|[Nn]ot allowed"):
            evaluator.evaluate("evil_func(1)")

    def test_division_by_zero(self, evaluator):
        with pytest.raises((ValueError, ZeroDivisionError)):
            evaluator.evaluate("1 / 0")

    def test_evaluate_safe_returns_default(self, evaluator):
        """Test evaluate_safe returns default on error."""
        assert evaluator.evaluate_safe("", default=42.0) == 42.0
        assert evaluator.evaluate_safe("invalid syntax +", default=-1.0) == -1.0

    def test_evaluate_as_bool_with_error(self, evaluator):
        """Test evaluate_as_bool with various inputs."""
        # Unknown variable should raise
        with pytest.raises(ValueError):
            evaluator.evaluate_as_bool("unknown_var")


class TestSecurity:
    """Test security restrictions."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_no_import(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("__import__('os')")

    def test_no_eval(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("eval('1+1')")

    def test_no_exec(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("exec('print(1)')")

    def test_no_attribute_access(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("'hello'.upper()")

    def test_no_subscript(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("[1,2,3][0]")

    def test_no_list_comp(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("[x for x in range(10)]")


class TestMathFunctionsInConditions:
    """Test math functions used in boolean conditions (TASK-060 new capability)."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"width": 7.8, "count": 15})
        return e

    def test_floor_in_condition(self, evaluator):
        """Test floor(width) > 5."""
        assert evaluator.evaluate_as_bool("floor(width) > 5") is True
        assert evaluator.evaluate_as_bool("floor(width) > 8") is False

    def test_ceil_in_condition(self, evaluator):
        """Test ceil(width) >= 8."""
        assert evaluator.evaluate_as_bool("ceil(width) >= 8") is True

    def test_sqrt_in_condition(self, evaluator):
        """Test sqrt(count) < 4."""
        assert evaluator.evaluate_as_bool("sqrt(count) < 4") is True
        assert evaluator.evaluate_as_bool("sqrt(count) < 3") is False

    def test_complex_condition(self, evaluator):
        """Test complex condition with multiple functions."""
        assert evaluator.evaluate_as_bool("floor(width) > 5 and ceil(width) < 10") is True


class TestRealWorldExamples:
    """Test real-world workflow scenarios."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_phone_workflow_screen_depth(self, evaluator):
        """Test phone workflow screen depth calculation."""
        evaluator.set_context({"depth": 0.12})
        result = evaluator.evaluate("depth * 0.9")
        assert abs(result - 0.108) < 0.001

    def test_table_workflow_plank_count(self, evaluator):
        """Test picnic table plank count calculation."""
        evaluator.set_context({"table_width": 1.8, "plank_width": 0.12})
        result = evaluator.evaluate("floor(table_width / plank_width)")
        assert result == 15.0

    def test_mode_check(self, evaluator):
        """Test mode switching condition."""
        evaluator.set_context({"current_mode": "OBJECT"})
        assert evaluator.evaluate_as_bool("current_mode != 'EDIT'") is True
        evaluator.update_context({"current_mode": "EDIT"})
        assert evaluator.evaluate_as_bool("current_mode != 'EDIT'") is False

    def test_selection_based_workflow(self, evaluator):
        """Test selection-based workflow condition."""
        evaluator.set_context({"has_selection": True, "selected_count": 5})
        assert evaluator.evaluate_as_bool("has_selection and selected_count > 0") is True

    def test_conditional_parameter(self, evaluator):
        """Test ternary for conditional parameter value."""
        evaluator.set_context({"is_detailed": True, "base_segments": 4})
        result = evaluator.evaluate("base_segments * 2 if is_detailed else base_segments")
        assert result == 8.0


class TestEvaluateAsFloat:
    """Test evaluate_as_float method."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"x": 5.0})
        return e

    def test_numeric_result(self, evaluator):
        assert evaluator.evaluate_as_float("x * 2") == 10.0

    def test_boolean_to_float(self, evaluator):
        """Test that bool result is converted to float."""
        # True -> 1.0, False -> 0.0
        assert evaluator.evaluate_as_float("x > 0") == 1.0
        assert evaluator.evaluate_as_float("x < 0") == 0.0

    def test_string_raises(self, evaluator):
        """Test that string result raises ValueError."""
        evaluator.set_context({"name": "test"})
        # String comparison returns bool, which should convert fine
        # But just string by itself would be an issue
        # Actually, just referencing a string variable should raise
        with pytest.raises(ValueError):
            evaluator.evaluate_as_float("name")
