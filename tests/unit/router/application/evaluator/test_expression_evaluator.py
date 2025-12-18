"""
Tests for Expression Evaluator.

TASK-041-7
"""

import pytest
import math
from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator


class TestExpressionEvaluatorInit:
    """Test evaluator initialization."""

    def test_init_empty_context(self):
        evaluator = ExpressionEvaluator()
        assert evaluator.get_context() == {}

    def test_set_context_dimensions(self):
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"dimensions": [2.0, 4.0, 0.5]})

        context = evaluator.get_context()
        assert context["width"] == 2.0
        assert context["height"] == 4.0
        assert context["depth"] == 0.5
        assert context["min_dim"] == 0.5
        assert context["max_dim"] == 4.0

    def test_set_context_direct_values(self):
        evaluator = ExpressionEvaluator()
        evaluator.set_context({
            "width": 3.0,
            "height": 6.0,
            "depth": 1.0,
        })

        context = evaluator.get_context()
        assert context["width"] == 3.0
        assert context["height"] == 6.0
        assert context["depth"] == 1.0

    def test_set_context_proportions(self):
        evaluator = ExpressionEvaluator()
        evaluator.set_context({
            "proportions": {
                "aspect_xy": 0.5,
                "is_flat": True,
                "is_tall": False,
            }
        })

        context = evaluator.get_context()
        assert context["proportions_aspect_xy"] == 0.5
        assert context["proportions_is_flat"] == 1.0
        assert context["proportions_is_tall"] == 0.0


class TestBasicArithmetic:
    """Test basic arithmetic operations."""

    @pytest.fixture
    def evaluator(self):
        e = ExpressionEvaluator()
        e.set_context({"width": 2.0, "height": 4.0, "depth": 0.5})
        return e

    def test_addition(self, evaluator):
        assert evaluator.evaluate("2 + 3") == 5.0
        assert evaluator.evaluate("width + height") == 6.0

    def test_subtraction(self, evaluator):
        assert evaluator.evaluate("10 - 3") == 7.0
        assert evaluator.evaluate("height - width") == 2.0

    def test_multiplication(self, evaluator):
        assert evaluator.evaluate("3 * 4") == 12.0
        assert evaluator.evaluate("width * 0.5") == 1.0
        assert evaluator.evaluate("width * height") == 8.0

    def test_division(self, evaluator):
        assert evaluator.evaluate("10 / 2") == 5.0
        assert evaluator.evaluate("height / width") == 2.0

    def test_power(self, evaluator):
        assert evaluator.evaluate("2 ** 3") == 8.0
        assert evaluator.evaluate("width ** 2") == 4.0

    def test_modulo(self, evaluator):
        assert evaluator.evaluate("10 % 3") == 1.0

    def test_floor_division(self, evaluator):
        assert evaluator.evaluate("10 // 3") == 3.0

    def test_unary_minus(self, evaluator):
        assert evaluator.evaluate("-5") == -5.0
        assert evaluator.evaluate("-width") == -2.0

    def test_unary_plus(self, evaluator):
        assert evaluator.evaluate("+5") == 5.0

    def test_complex_expression(self, evaluator):
        assert evaluator.evaluate("width * 2 + height / 2") == 6.0
        assert evaluator.evaluate("(width + height) * depth") == 3.0


class TestMathFunctions:
    """Test math function support."""

    @pytest.fixture
    def evaluator(self):
        e = ExpressionEvaluator()
        e.set_context({"width": 2.0, "height": 4.0, "depth": 0.5})
        return e

    def test_abs(self, evaluator):
        assert evaluator.evaluate("abs(-5)") == 5.0
        assert evaluator.evaluate("abs(width - height)") == 2.0

    def test_min(self, evaluator):
        assert evaluator.evaluate("min(3, 5)") == 3.0
        assert evaluator.evaluate("min(width, height)") == 2.0
        assert evaluator.evaluate("min(width, height, depth)") == 0.5

    def test_max(self, evaluator):
        assert evaluator.evaluate("max(3, 5)") == 5.0
        assert evaluator.evaluate("max(width, height)") == 4.0

    def test_round(self, evaluator):
        assert evaluator.evaluate("round(3.7)") == 4.0
        assert evaluator.evaluate("round(3.2)") == 3.0

    def test_floor(self, evaluator):
        assert evaluator.evaluate("floor(3.7)") == 3.0
        assert evaluator.evaluate("floor(3.2)") == 3.0

    def test_ceil(self, evaluator):
        assert evaluator.evaluate("ceil(3.2)") == 4.0
        assert evaluator.evaluate("ceil(3.7)") == 4.0

    def test_sqrt(self, evaluator):
        assert evaluator.evaluate("sqrt(4)") == 2.0
        assert evaluator.evaluate("sqrt(width)") == pytest.approx(math.sqrt(2.0))

    def test_nested_functions(self, evaluator):
        assert evaluator.evaluate("min(abs(-5), max(2, 3))") == 3.0


class TestResolveParamValue:
    """Test parameter value resolution."""

    @pytest.fixture
    def evaluator(self):
        e = ExpressionEvaluator()
        e.set_context({"width": 2.0, "height": 4.0, "depth": 0.1})
        return e

    def test_calculate_expression(self, evaluator):
        result = evaluator.resolve_param_value("$CALCULATE(width * 0.5)")
        assert result == 1.0

    def test_calculate_complex(self, evaluator):
        result = evaluator.resolve_param_value("$CALCULATE(min(width, height) * depth)")
        assert result == 0.2

    def test_simple_variable(self, evaluator):
        result = evaluator.resolve_param_value("$width")
        assert result == 2.0

    def test_non_string_passthrough(self, evaluator):
        assert evaluator.resolve_param_value(42) == 42
        assert evaluator.resolve_param_value(3.14) == 3.14
        assert evaluator.resolve_param_value(None) is None

    def test_plain_string_passthrough(self, evaluator):
        assert evaluator.resolve_param_value("plain string") == "plain string"
        assert evaluator.resolve_param_value("CUBE") == "CUBE"

    def test_undefined_variable(self, evaluator):
        # Should return original value if variable not found
        result = evaluator.resolve_param_value("$unknown_var")
        assert result == "$unknown_var"

    def test_invalid_expression(self, evaluator):
        # Should return original value if expression fails
        result = evaluator.resolve_param_value("$CALCULATE(invalid syntax +++)")
        assert result == "$CALCULATE(invalid syntax +++)"


class TestResolveParams:
    """Test batch parameter resolution."""

    @pytest.fixture
    def evaluator(self):
        e = ExpressionEvaluator()
        e.set_context({"width": 2.0, "height": 4.0, "depth": 0.1})
        return e

    def test_resolve_params_basic(self, evaluator):
        params = {
            "size": "$CALCULATE(width * 0.5)",
            "mode": "EDIT",
            "count": 5,
        }
        resolved = evaluator.resolve_params(params)

        assert resolved["size"] == 1.0
        assert resolved["mode"] == "EDIT"
        assert resolved["count"] == 5

    def test_resolve_params_list(self, evaluator):
        params = {
            "scale": [1.0, "$CALCULATE(height / 2)", "$depth"],
        }
        resolved = evaluator.resolve_params(params)

        assert resolved["scale"] == [1.0, 2.0, 0.1]

    def test_resolve_params_nested_dict(self, evaluator):
        params = {
            "outer": {
                "inner": "$CALCULATE(width + 1)",
            }
        }
        resolved = evaluator.resolve_params(params)

        assert resolved["outer"]["inner"] == 3.0


class TestSafety:
    """Test that dangerous operations are blocked."""

    @pytest.fixture
    def evaluator(self):
        return ExpressionEvaluator()

    def test_no_imports(self, evaluator):
        result = evaluator.evaluate("__import__('os')")
        assert result is None

    def test_no_eval(self, evaluator):
        result = evaluator.evaluate("eval('1+1')")
        assert result is None

    def test_no_exec(self, evaluator):
        result = evaluator.evaluate("exec('x=1')")
        assert result is None

    def test_no_attribute_access(self, evaluator):
        result = evaluator.evaluate("'string'.upper()")
        assert result is None

    def test_no_subscript(self, evaluator):
        result = evaluator.evaluate("[1,2,3][0]")
        assert result is None

    def test_only_whitelist_functions(self, evaluator):
        # open, print, etc. should fail
        result = evaluator.evaluate("open('file.txt')")
        assert result is None

        result = evaluator.evaluate("print('hello')")
        assert result is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def evaluator(self):
        return ExpressionEvaluator()

    def test_empty_expression(self, evaluator):
        assert evaluator.evaluate("") is None
        assert evaluator.evaluate("   ") is None

    def test_syntax_error(self, evaluator):
        assert evaluator.evaluate("2 +") is None
        assert evaluator.evaluate("((2 + 3)") is None

    def test_division_by_zero(self, evaluator):
        # Python raises ZeroDivisionError, we return None
        result = evaluator.evaluate("1 / 0")
        assert result is None

    def test_variable_not_found(self, evaluator):
        result = evaluator.evaluate("unknown_variable * 2")
        assert result is None

    def test_negative_sqrt(self, evaluator):
        # sqrt of negative should fail
        result = evaluator.evaluate("sqrt(-1)")
        assert result is None

    def test_very_large_number(self, evaluator):
        result = evaluator.evaluate("10 ** 100")
        assert result == pytest.approx(10 ** 100)


class TestRealWorldExamples:
    """Test real-world workflow parameter examples."""

    def test_phone_workflow_screen_depth(self):
        """Test calculating screen depth for phone workflow."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"depth": 0.1})

        result = evaluator.resolve_param_value("$CALCULATE(depth * 0.5)")
        assert result == 0.05

    def test_bevel_width_from_dimensions(self):
        """Test calculating bevel width from object dimensions."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"dimensions": [2.0, 4.0, 0.5]})

        # 5% of smallest dimension
        result = evaluator.resolve_param_value("$CALCULATE(min_dim * 0.05)")
        assert result == 0.025

    def test_extrude_from_height(self):
        """Test calculating extrude distance from height."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"height": 10.0})

        # 10% of height
        result = evaluator.resolve_param_value("$CALCULATE(height * 0.1)")
        assert result == 1.0

    def test_scale_calculation(self):
        """Test calculating scale values."""
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"width": 2.0, "height": 4.0, "depth": 0.5})

        params = {
            "scale": [
                "$CALCULATE(width * 0.8)",
                "$CALCULATE(height * 0.8)",
                "$CALCULATE(depth * 0.8)",
            ]
        }
        resolved = evaluator.resolve_params(params)

        assert resolved["scale"] == [1.6, 3.2, 0.4]
