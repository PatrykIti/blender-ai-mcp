"""
Expression Evaluator.

Safe expression evaluator for workflow parameters.
Supports $CALCULATE(...) expressions with arithmetic and math functions.

TASK-041-7
"""

import re
import ast
import math
import operator
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ExpressionEvaluator:
    """Safe expression evaluator for workflow parameters.

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

    # Allowed functions (whitelist) - TASK-056-1: Extended with 13 new functions
    FUNCTIONS = {
        # Basic functions
        "abs": abs,
        "min": min,
        "max": max,
        "round": round,
        "floor": math.floor,
        "ceil": math.ceil,
        "sqrt": math.sqrt,
        "trunc": math.trunc,  # TASK-056-1: Integer truncation

        # Trigonometric functions (existing)
        "sin": math.sin,
        "cos": math.cos,

        # Trigonometric functions (TASK-056-1: NEW)
        "tan": math.tan,           # Tangent
        "asin": math.asin,         # Arc sine (inverse sine)
        "acos": math.acos,         # Arc cosine (inverse cosine)
        "atan": math.atan,         # Arc tangent (inverse tangent)
        "atan2": math.atan2,       # Two-argument arc tangent (handles quadrants)
        "degrees": math.degrees,   # Convert radians to degrees
        "radians": math.radians,   # Convert degrees to radians

        # Logarithmic functions (TASK-056-1: NEW)
        "log": math.log,           # Natural logarithm (base e)
        "log10": math.log10,       # Base-10 logarithm
        "exp": math.exp,           # e^x (exponential)

        # Advanced functions (TASK-056-1: NEW)
        "pow": pow,                # Power (alternative to ** operator)
        "hypot": math.hypot,       # Hypotenuse: sqrt(x^2 + y^2 + ...)
    }

    # Pattern for $CALCULATE(...)
    CALCULATE_PATTERN = re.compile(r"^\$CALCULATE\((.+)\)$")

    # Pattern for simple $variable reference
    VARIABLE_PATTERN = re.compile(r"^\$([a-zA-Z_][a-zA-Z0-9_]*)$")

    def __init__(self):
        """Initialize expression evaluator."""
        self._context: Dict[str, float] = {}

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
        self._context = {}

        # Flatten context for easy access
        if "dimensions" in context:
            dims = context["dimensions"]
            if isinstance(dims, (list, tuple)) and len(dims) >= 3:
                self._context["width"] = float(dims[0])
                self._context["height"] = float(dims[1])
                self._context["depth"] = float(dims[2])
                self._context["min_dim"] = float(min(dims[:3]))
                self._context["max_dim"] = float(max(dims[:3]))

        # Handle direct width/height/depth
        for key in ["width", "height", "depth"]:
            if key in context and isinstance(context[key], (int, float)):
                self._context[key] = float(context[key])

        # Handle proportions
        if "proportions" in context:
            props = context["proportions"]
            if isinstance(props, dict):
                for key, value in props.items():
                    if isinstance(value, (int, float)):
                        self._context[f"proportions_{key}"] = float(value)
                    elif isinstance(value, bool):
                        self._context[f"proportions_{key}"] = 1.0 if value else 0.0

        # Allow any numeric values from context
        for key, value in context.items():
            if key not in self._context and isinstance(value, (int, float)):
                self._context[key] = float(value)

    def get_context(self) -> Dict[str, float]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        return dict(self._context)

    def evaluate(self, expression: str) -> Optional[float]:
        """Evaluate a mathematical expression.

        Args:
            expression: Expression string (without $CALCULATE wrapper).
                       Examples: "width * 0.5", "min(width, height)", "depth / 2"

        Returns:
            Evaluated result or None if invalid.
        """
        if not expression or not expression.strip():
            return None

        expression = expression.strip()

        try:
            result = self._safe_eval(expression)
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

        Examples:
            resolve_param_value("$CALCULATE(width * 0.1)") -> 0.2
            resolve_param_value("$width") -> 2.0
            resolve_param_value(42) -> 42
            resolve_param_value("plain string") -> "plain string"
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
            if var_name in self._context:
                return self._context[var_name]
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
                # Handle list values (e.g., scale: [1.0, "$CALCULATE(width)", 0.1])
                resolved[key] = [self.resolve_param_value(v) for v in value]
            elif isinstance(value, dict):
                # Handle nested dicts
                resolved[key] = self.resolve_params(value)
            else:
                resolved[key] = self.resolve_param_value(value)
        return resolved

    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate expression using AST parsing.

        Only allows arithmetic operations and whitelisted functions.

        Args:
            expression: Mathematical expression string.

        Returns:
            Evaluated float result.

        Raises:
            ValueError: If expression contains disallowed constructs.
            SyntaxError: If expression has invalid syntax.
        """
        # Replace variable names with values
        modified_expression = expression
        for var_name, var_value in self._context.items():
            # Use word boundaries to avoid partial replacements
            modified_expression = re.sub(
                rf"\b{re.escape(var_name)}\b",
                str(var_value),
                modified_expression,
            )

        # Parse AST
        try:
            tree = ast.parse(modified_expression, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {e}")

        # Validate and evaluate
        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> float:
        """Recursively evaluate AST node.

        Args:
            node: AST node to evaluate.

        Returns:
            Evaluated float value.

        Raises:
            ValueError: If node type is not allowed.
        """
        # Constant (Python 3.8+)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Invalid constant type: {type(node.value)}")

        # Num (Python 3.7 fallback)
        if isinstance(node, ast.Num):
            return float(node.n)

        # Binary operation
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            op_map = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.FloorDiv: operator.floordiv,
            }

            op_type = type(node.op)
            if op_type in op_map:
                return op_map[op_type](left, right)
            raise ValueError(f"Unsupported operator: {op_type.__name__}")

        # Unary operation
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.UAdd):
                return operand
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

        # Function call
        if isinstance(node, ast.Call):
            # Get function name
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls allowed")

            func_name = node.func.id
            if func_name not in self.FUNCTIONS:
                raise ValueError(f"Function not allowed: {func_name}")

            # Evaluate arguments
            args = [self._eval_node(arg) for arg in node.args]

            # Call function
            return float(self.FUNCTIONS[func_name](*args))

        # Name (variable) - should have been replaced, but handle anyway
        if isinstance(node, ast.Name):
            var_name = node.id
            if var_name in self._context:
                return self._context[var_name]
            raise ValueError(f"Unknown variable: {var_name}")

        raise ValueError(f"Unsupported AST node: {type(node).__name__}")

    def resolve_computed_parameters(
        self,
        schemas: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve all computed parameters in dependency order.

        TASK-056-5: Evaluates computed parameter expressions using topological
        sorting to ensure dependencies are resolved before dependents.

        Args:
            schemas: Dictionary of parameter name -> ParameterSchema.
            context: Initial parameter values (non-computed parameters).

        Returns:
            Dictionary with all parameters (non-computed + computed).

        Raises:
            ValueError: If circular dependency detected or unknown variable.

        Example:
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
            # result = {"width": 2.0, "height": 1.0, "aspect_ratio": 2.0}
        """
        resolved = dict(context)

        # Extract computed parameters
        computed_params = {
            name: schema
            for name, schema in schemas.items()
            if hasattr(schema, "computed") and schema.computed
        }

        if not computed_params:
            return resolved

        # Build dependency graph
        graph = {
            name: (schema.depends_on if hasattr(schema, "depends_on") else [])
            for name, schema in computed_params.items()
        }

        # Topological sort
        sorted_params = self._topological_sort(graph)

        # Resolve in dependency order
        for param_name in sorted_params:
            schema = computed_params[param_name]

            # Update context with current resolved values
            self.set_context(resolved)

            # Evaluate computed expression
            expr = schema.computed
            value = self.evaluate(expr)

            if value is None:
                raise ValueError(
                    f"Failed to compute parameter '{param_name}' "
                    f"with expression: {expr}"
                )

            resolved[param_name] = value
            logger.debug(
                f"Computed parameter '{param_name}' = {value} (from: {expr})"
            )

        return resolved

    def _topological_sort(self, graph: Dict[str, list]) -> list:
        """Perform topological sort on dependency graph.

        TASK-056-5: Implements Kahn's algorithm for topological sorting.

        Args:
            graph: Dictionary mapping node -> list of dependencies.
                   Keys are nodes, values are lists of nodes they depend on.
                   Dependencies may include nodes not in the graph (external deps).

        Returns:
            List of nodes in topologically sorted order.

        Raises:
            ValueError: If circular dependency detected.
        """
        # Calculate in-degrees (count only dependencies that are IN the graph)
        in_degree = {}
        for node, deps in graph.items():
            # Only count dependencies that are themselves in the graph
            in_degree[node] = sum(1 for dep in deps if dep in graph)

        # Queue of nodes with no unmet dependencies (in-degree 0)
        queue = [node for node, degree in in_degree.items() if degree == 0]
        sorted_nodes = []

        while queue:
            # Take a node with no unmet dependencies
            node = queue.pop(0)
            sorted_nodes.append(node)

            # For every other node, check if it depends on this node
            for other_node in graph:
                if node in graph[other_node]:
                    # Reduce dependency count (we've processed 'node')
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0:
                        # All dependencies met, can process
                        queue.append(other_node)

        # Check for cycles
        if len(sorted_nodes) != len(graph):
            remaining = set(graph.keys()) - set(sorted_nodes)
            raise ValueError(
                f"Circular dependency detected in computed parameters: {remaining}"
            )

        return sorted_nodes
