"""
Unit tests for extended ExpressionEvaluator features.

Tests TASK-056-1: 13 new math functions
Tests TASK-056-5: Computed parameters system
"""

import pytest
import math
from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator
from server.router.domain.entities.parameter import ParameterSchema


class TestExtendedMathFunctions:
    """Test TASK-056-1: 13 new math functions."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator with test context."""
        ev = ExpressionEvaluator()
        ev.set_context({
            "x": 2.0,
            "y": 3.0,
            "angle": 0.5,  # radians
        })
        return ev

    def test_trunc(self, evaluator):
        """Test trunc function."""
        assert evaluator.evaluate("trunc(3.7)") == 3.0
        assert evaluator.evaluate("trunc(-3.7)") == -3.0

    def test_tan(self, evaluator):
        """Test tangent function."""
        result = evaluator.evaluate("tan(angle)")
        expected = math.tan(0.5)
        assert abs(result - expected) < 1e-10

    def test_asin(self, evaluator):
        """Test arc sine function."""
        result = evaluator.evaluate("asin(0.5)")
        expected = math.asin(0.5)
        assert abs(result - expected) < 1e-10

    def test_acos(self, evaluator):
        """Test arc cosine function."""
        result = evaluator.evaluate("acos(0.5)")
        expected = math.acos(0.5)
        assert abs(result - expected) < 1e-10

    def test_atan(self, evaluator):
        """Test arc tangent function."""
        result = evaluator.evaluate("atan(1.0)")
        expected = math.atan(1.0)
        assert abs(result - expected) < 1e-10

    def test_atan2(self, evaluator):
        """Test two-argument arc tangent."""
        result = evaluator.evaluate("atan2(y, x)")
        expected = math.atan2(3.0, 2.0)
        assert abs(result - expected) < 1e-10

    def test_degrees(self, evaluator):
        """Test radians to degrees conversion."""
        result = evaluator.evaluate("degrees(angle)")
        expected = math.degrees(0.5)
        assert abs(result - expected) < 1e-10

    def test_radians(self, evaluator):
        """Test degrees to radians conversion."""
        result = evaluator.evaluate("radians(90)")
        expected = math.radians(90)
        assert abs(result - expected) < 1e-10

    def test_log(self, evaluator):
        """Test natural logarithm."""
        result = evaluator.evaluate("log(x)")
        expected = math.log(2.0)
        assert abs(result - expected) < 1e-10

    def test_log10(self, evaluator):
        """Test base-10 logarithm."""
        result = evaluator.evaluate("log10(100)")
        assert abs(result - 2.0) < 1e-10

    def test_exp(self, evaluator):
        """Test exponential function."""
        result = evaluator.evaluate("exp(1)")
        expected = math.e
        assert abs(result - expected) < 1e-10

    def test_pow(self, evaluator):
        """Test power function."""
        result = evaluator.evaluate("pow(x, y)")
        expected = pow(2.0, 3.0)
        assert abs(result - expected) < 1e-10

    def test_hypot(self, evaluator):
        """Test hypotenuse function."""
        result = evaluator.evaluate("hypot(x, y)")
        expected = math.hypot(2.0, 3.0)
        assert abs(result - expected) < 1e-10

    def test_complex_expression_with_new_functions(self, evaluator):
        """Test complex expression using multiple new functions."""
        # Calculate angle from opposite and adjacent sides
        result = evaluator.evaluate("degrees(atan2(y, x))")
        expected = math.degrees(math.atan2(3.0, 2.0))
        assert abs(result - expected) < 1e-10


class TestComputedParameters:
    """Test TASK-056-5: Computed parameters system."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator for computed parameter tests."""
        return ExpressionEvaluator()

    def test_simple_computed_parameter(self, evaluator):
        """Test basic computed parameter resolution."""
        schemas = {
            "width": ParameterSchema(name="width", type="float"),
            "height": ParameterSchema(name="height", type="float"),
            "aspect_ratio": ParameterSchema(
                name="aspect_ratio",
                type="float",
                computed="width / height",
                depends_on=["width", "height"]
            )
        }

        context = {"width": 2.0, "height": 1.0}
        result = evaluator.resolve_computed_parameters(schemas, context)

        assert result["width"] == 2.0
        assert result["height"] == 1.0
        assert result["aspect_ratio"] == 2.0

    def test_computed_parameter_chain(self, evaluator):
        """Test chain of dependent computed parameters."""
        schemas = {
            "base": ParameterSchema(name="base", type="float"),
            "double": ParameterSchema(
                name="double",
                type="float",
                computed="base * 2",
                depends_on=["base"]
            ),
            "quadruple": ParameterSchema(
                name="quadruple",
                type="float",
                computed="double * 2",
                depends_on=["double"]
            )
        }

        context = {"base": 5.0}
        result = evaluator.resolve_computed_parameters(schemas, context)

        assert result["base"] == 5.0
        assert result["double"] == 10.0
        assert result["quadruple"] == 20.0

    def test_computed_parameter_with_math_functions(self, evaluator):
        """Test computed parameters using new math functions."""
        schemas = {
            "width": ParameterSchema(name="width", type="float"),
            "height": ParameterSchema(name="height", type="float"),
            "diagonal": ParameterSchema(
                name="diagonal",
                type="float",
                computed="hypot(width, height)",
                depends_on=["width", "height"]
            )
        }

        context = {"width": 3.0, "height": 4.0}
        result = evaluator.resolve_computed_parameters(schemas, context)

        assert result["diagonal"] == 5.0

    def test_circular_dependency_detection(self, evaluator):
        """Test that circular dependencies are detected."""
        schemas = {
            "a": ParameterSchema(
                name="a",
                type="float",
                computed="b * 2",
                depends_on=["b"]
            ),
            "b": ParameterSchema(
                name="b",
                type="float",
                computed="a * 2",
                depends_on=["a"]
            )
        }

        with pytest.raises(ValueError, match="Circular dependency"):
            evaluator.resolve_computed_parameters(schemas, {})

    def test_no_computed_parameters(self, evaluator):
        """Test resolution when no computed parameters exist."""
        schemas = {
            "width": ParameterSchema(name="width", type="float"),
            "height": ParameterSchema(name="height", type="float"),
        }

        context = {"width": 2.0, "height": 1.0}
        result = evaluator.resolve_computed_parameters(schemas, context)

        assert result == context

    def test_complex_computed_parameter_graph(self, evaluator):
        """Test complex dependency graph with multiple branches."""
        schemas = {
            "width": ParameterSchema(name="width", type="float"),
            "height": ParameterSchema(name="height", type="float"),
            "depth": ParameterSchema(name="depth", type="float"),
            "area": ParameterSchema(
                name="area",
                type="float",
                computed="width * depth",
                depends_on=["width", "depth"]
            ),
            "volume": ParameterSchema(
                name="volume",
                type="float",
                computed="area * height",
                depends_on=["area", "height"]
            ),
            "diagonal": ParameterSchema(
                name="diagonal",
                type="float",
                computed="hypot(width, depth)",
                depends_on=["width", "depth"]
            )
        }

        context = {"width": 2.0, "height": 3.0, "depth": 4.0}
        result = evaluator.resolve_computed_parameters(schemas, context)

        assert result["area"] == 8.0
        assert result["volume"] == 24.0
        assert abs(result["diagonal"] - math.hypot(2.0, 4.0)) < 1e-10


class TestTopologicalSort:
    """Test topological sorting algorithm."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator for topological sort tests."""
        return ExpressionEvaluator()

    def test_simple_linear_graph(self, evaluator):
        """Test sorting of simple linear dependency graph."""
        graph = {
            "a": [],
            "b": ["a"],
            "c": ["b"]
        }

        result = evaluator._topological_sort(graph)

        # a must come before b, b must come before c
        assert result.index("a") < result.index("b")
        assert result.index("b") < result.index("c")

    def test_parallel_branches(self, evaluator):
        """Test sorting with parallel independent branches."""
        graph = {
            "a": [],
            "b": ["a"],
            "c": ["a"],
            "d": ["b", "c"]
        }

        result = evaluator._topological_sort(graph)

        # a must come first
        assert result[0] == "a"
        # d must come last
        assert result[-1] == "d"
        # b and c must come before d
        assert result.index("b") < result.index("d")
        assert result.index("c") < result.index("d")

    def test_circular_dependency(self, evaluator):
        """Test circular dependency detection."""
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["a"]
        }

        with pytest.raises(ValueError, match="Circular dependency"):
            evaluator._topological_sort(graph)

    def test_empty_graph(self, evaluator):
        """Test sorting of empty graph."""
        graph = {}
        result = evaluator._topological_sort(graph)
        assert result == []
