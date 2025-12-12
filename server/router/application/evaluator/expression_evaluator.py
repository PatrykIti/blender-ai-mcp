"""
Expression Evaluator.

Safe expression evaluator for workflow parameters.
Supports $CALCULATE(...) expressions with arithmetic and math functions.

TASK-041-7: Original implementation
TASK-060: Refactored to delegate to UnifiedEvaluator.
"""

import re
import logging
from typing import Dict, Any, Optional

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator

logger = logging.getLogger(__name__)


class ExpressionEvaluator:
    """Safe expression evaluator for workflow parameters.

    This is a wrapper around UnifiedEvaluator that provides:
    - $CALCULATE(...) pattern matching
    - $variable direct references
    - Context flattening (dimensions -> width/height/depth)
    - Backward-compatible API

    TASK-060: Now delegates evaluation to UnifiedEvaluator.

    Supports:
    - Basic arithmetic: +, -, *, /, **, %
    - Math functions: abs, min, max, round, floor, ceil, sqrt, trunc
    - Trigonometric: sin, cos, tan, asin, acos, atan, atan2, degrees, radians
    - Logarithmic: log, log10, exp
    - Advanced: pow, hypot
    - Variable references: width, height, depth, min_dim, max_dim, etc.

    Does NOT support:
    - Arbitrary Python code
    - Imports
    - Function calls beyond whitelist
    - Attribute access
    - Subscript access

    Example:
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"width": 2.0, "height": 4.0, "leg_angle": 1.0})
        result = evaluator.evaluate("width * 0.5")  # -> 1.0
        result = evaluator.resolve_param_value("$CALCULATE(height / width)")  # -> 2.0
        result = evaluator.resolve_param_value("$CALCULATE(sin(leg_angle))")  # -> ~0.841
        result = evaluator.resolve_param_value("$CALCULATE(atan2(height, width))")  # -> ~1.107
        result = evaluator.resolve_param_value("$CALCULATE(log10(100))")  # -> 2.0
    """

    # Pattern for $CALCULATE(...)
    CALCULATE_PATTERN = re.compile(r"^\$CALCULATE\((.+)\)$")

    # Pattern for simple $variable reference
    VARIABLE_PATTERN = re.compile(r"^\$([a-zA-Z_][a-zA-Z0-9_]*)$")

    # Expose FUNCTIONS for backward compatibility (some code checks this)
    FUNCTIONS = UnifiedEvaluator.FUNCTIONS

    def __init__(self):
        """Initialize expression evaluator."""
        self._unified = UnifiedEvaluator()

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dict with variable values (dimensions, proportions, etc.)

        Expected keys:
            - dimensions: List[float] of [x, y, z]
            - width, height, depth: Individual dimensions
            - min_dim, max_dim: Min/max of dimensions
            - proportions: Dict with aspect ratios
        """
        flat_context: Dict[str, Any] = {}

        # Flatten context for easy access
        if "dimensions" in context:
            dims = context["dimensions"]
            if isinstance(dims, (list, tuple)) and len(dims) >= 3:
                flat_context["width"] = float(dims[0])
                flat_context["height"] = float(dims[1])
                flat_context["depth"] = float(dims[2])
                flat_context["min_dim"] = float(min(dims[:3]))
                flat_context["max_dim"] = float(max(dims[:3]))

        # Handle direct width/height/depth
        for key in ["width", "height", "depth"]:
            if key in context and isinstance(context[key], (int, float)):
                flat_context[key] = float(context[key])

        # Handle proportions
        if "proportions" in context:
            props = context["proportions"]
            if isinstance(props, dict):
                for key, value in props.items():
                    if isinstance(value, (int, float)):
                        flat_context[f"proportions_{key}"] = float(value)
                    elif isinstance(value, bool):
                        flat_context[f"proportions_{key}"] = 1.0 if value else 0.0

        # Allow any numeric/string values from context
        for key, value in context.items():
            if key not in flat_context:
                if isinstance(value, (int, float)):
                    flat_context[key] = float(value)
                elif isinstance(value, bool):
                    flat_context[key] = 1.0 if value else 0.0
                elif isinstance(value, str):
                    flat_context[key] = value

        self._unified.set_context(flat_context)

    def get_context(self) -> Dict[str, float]:
        """Get current evaluation context (numeric values only).

        Returns:
            Copy of current context dictionary with only numeric values.
            Strings are filtered out for backward compatibility.
        """
        ctx = self._unified.get_context()
        return {k: v for k, v in ctx.items() if isinstance(v, (int, float))}

    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values (merge).

        Args:
            updates: Dictionary with values to add/update.
        """
        self._unified.update_context(updates)

    def evaluate(self, expression: str) -> Optional[float]:
        """Evaluate a mathematical expression.

        Args:
            expression: Expression string (without $CALCULATE wrapper).

        Returns:
            Evaluated result or None if invalid.
        """
        if not expression or not expression.strip():
            return None

        try:
            result = self._unified.evaluate_as_float(expression)
            logger.debug(f"Expression '{expression}' evaluated to {result}")
            return result
        except Exception as e:
            logger.warning(f"Expression evaluation failed: '{expression}' - {e}")
            return None

    def resolve_param_value(self, value: Any) -> Any:
        """Resolve a parameter value, evaluating $CALCULATE if present.

        Args:
            value: Parameter value (may contain $CALCULATE or $variable).

        Returns:
            Resolved value. Original value if resolution fails.
        """
        if not isinstance(value, str):
            return value

        # Check for $CALCULATE(...)
        calc_match = self.CALCULATE_PATTERN.match(value)
        if calc_match:
            expression = calc_match.group(1)
            result = self.evaluate(expression)
            if result is not None:
                return result
            logger.warning(f"Failed to evaluate $CALCULATE, returning original: {value}")
            return value

        # Check for simple $variable reference
        var_match = self.VARIABLE_PATTERN.match(value)
        if var_match:
            var_name = var_match.group(1)
            var_value = self._unified.get_variable(var_name)
            if var_value is not None:
                return var_value
            logger.warning(f"Variable not found in context: ${var_name}")
            return value

        return value

    def resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all parameters in a dictionary.

        Args:
            params: Dictionary of parameter name -> value.

        Returns:
            New dictionary with resolved values.
        """
        resolved = {}
        for key, value in params.items():
            if isinstance(value, list):
                resolved[key] = [self.resolve_param_value(v) for v in value]
            elif isinstance(value, dict):
                resolved[key] = self.resolve_params(value)
            else:
                resolved[key] = self.resolve_param_value(value)
        return resolved

    def resolve_computed_parameters(
        self,
        schemas: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve all computed parameters in dependency order.

        TASK-056-5: Delegates to UnifiedEvaluator.

        Args:
            schemas: Dictionary of parameter name -> ParameterSchema.
            context: Initial parameter values (non-computed parameters).

        Returns:
            Dictionary with all parameters (non-computed + computed).

        Raises:
            ValueError: If circular dependency detected or unknown variable.
        """
        return self._unified.resolve_computed_parameters(schemas, context)

    def _topological_sort(self, graph: Dict[str, list]) -> list:
        """Perform topological sort on dependency graph.

        TASK-056-5: Delegates to UnifiedEvaluator for backward compatibility.

        Args:
            graph: Dictionary mapping node -> list of dependencies.

        Returns:
            List of nodes in topologically sorted order.

        Raises:
            ValueError: If circular dependency detected.
        """
        return self._unified._topological_sort(graph)
