"""
Unified Expression Evaluator.

AST-based evaluator for mathematical expressions, comparisons, and logic.
Single source of truth for all evaluation in the Router system.

TASK-060: Consolidates ExpressionEvaluator and ConditionEvaluator logic.
"""

import ast
import math
import operator
import logging
from typing import Dict, Any, Optional, List

from server.router.domain.interfaces.i_expression_evaluator import IExpressionEvaluator

logger = logging.getLogger(__name__)


class UnifiedEvaluator(IExpressionEvaluator):
    """AST-based evaluator for math, comparisons, and logic.

    Returns appropriate type based on expression:
    - Arithmetic: float
    - Comparisons: float (1.0 for True, 0.0 for False)
    - String literals: str (for string comparisons)

    Supports:
    - Arithmetic: +, -, *, /, //, %, **
    - Math functions: abs, min, max, floor, ceil, sqrt, sin, cos, etc. (22 total)
    - Comparisons: <, <=, >, >=, ==, !=
    - Chained comparisons: 0 < x < 10
    - Logic: and, or, not (with short-circuit evaluation)
    - Ternary: x if condition else y
    - String comparisons: mode == 'EDIT'

    Security:
    - AST-based parsing (no eval/exec)
    - Function whitelist only
    - No attribute access, subscripting, or imports
    """

    # Allowed functions (whitelist) - from TASK-056-1
    FUNCTIONS: Dict[str, Any] = {
        # Basic functions
        "abs": abs,
        "min": min,
        "max": max,
        "round": round,
        "floor": math.floor,
        "ceil": math.ceil,
        "sqrt": math.sqrt,
        "trunc": math.trunc,
        # Trigonometric functions
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "degrees": math.degrees,
        "radians": math.radians,
        # Logarithmic functions
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        # Advanced functions
        "pow": pow,
        "hypot": math.hypot,
    }

    # Binary operators mapping
    BINARY_OPS: Dict[type, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    # Comparison operators mapping
    COMPARE_OPS: Dict[type, Any] = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
    }

    def __init__(self):
        """Initialize unified evaluator."""
        self._context: Dict[str, Any] = {}
        # Store original values for get_context() to return proper types
        self._original_context: Dict[str, Any] = {}

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dictionary with variable values.
                     Supports: int, float, bool, str values.
        """
        self._context = {}
        self._original_context = {}
        for key, value in context.items():
            if isinstance(value, bool):
                # CRITICAL: Check bool BEFORE int (bool is subclass of int)
                self._context[key] = 1.0 if value else 0.0
                self._original_context[key] = value  # Keep original bool
            elif isinstance(value, (int, float)):
                self._context[key] = float(value)
                self._original_context[key] = value
            elif isinstance(value, str):
                # Store strings for comparison (e.g., mode == 'EDIT')
                self._context[key] = value
                self._original_context[key] = value
            # Ignore other types (lists, dicts, etc.)

    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values.

        Args:
            updates: Dictionary with values to add/update.
        """
        for key, value in updates.items():
            if isinstance(value, bool):
                self._context[key] = 1.0 if value else 0.0
                self._original_context[key] = value
            elif isinstance(value, (int, float)):
                self._context[key] = float(value)
                self._original_context[key] = value
            elif isinstance(value, str):
                self._context[key] = value
                self._original_context[key] = value

    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary with original types preserved.
        """
        return dict(self._original_context)

    def get_variable(self, name: str) -> Optional[Any]:
        """Get variable value from context.

        Args:
            name: Variable name.

        Returns:
            Variable value or None if not found.
        """
        return self._context.get(name)

    def evaluate(self, expression: str) -> Any:
        """Evaluate expression and return result.

        Args:
            expression: Expression string to evaluate.

        Returns:
            Evaluated value (float for math, str for string literals).

        Raises:
            ValueError: If expression is invalid or uses disallowed constructs.
        """
        if not expression or not expression.strip():
            raise ValueError("Empty expression")

        expression = expression.strip()

        try:
            tree = ast.parse(expression, mode="eval")
            return self._eval_node(tree.body)
        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {e}")

    def evaluate_safe(self, expression: str, default: Any = 0.0) -> Any:
        """Evaluate expression with fallback on error.

        Args:
            expression: Expression string to evaluate.
            default: Value to return on error.

        Returns:
            Evaluated value or default on error.
        """
        try:
            return self.evaluate(expression)
        except Exception as e:
            logger.warning(f"Expression evaluation failed: '{expression}' - {e}")
            return default

    def evaluate_as_bool(self, expression: str) -> bool:
        """Evaluate expression and convert result to boolean.

        Args:
            expression: Expression string to evaluate.

        Returns:
            Boolean result.

        Raises:
            ValueError: If expression is invalid.
        """
        result = self.evaluate(expression)
        return bool(result)

    def evaluate_as_float(self, expression: str) -> float:
        """Evaluate expression and ensure float result.

        Args:
            expression: Expression string to evaluate.

        Returns:
            Float result.

        Raises:
            ValueError: If expression is invalid or result is not numeric.
        """
        result = self.evaluate(expression)
        if isinstance(result, str):
            raise ValueError(f"Expression returned string, expected numeric: {result}")
        return float(result)

    def _eval_node(self, node: ast.AST) -> Any:
        """Recursively evaluate AST node.

        Handles:
        - Constants (ast.Constant, ast.Num, ast.Str, ast.NameConstant)
        - Binary operations (ast.BinOp)
        - Unary operations (ast.UnaryOp) including 'not'
        - Comparisons (ast.Compare) including chained
        - Boolean operations (ast.BoolOp) with short-circuit
        - Ternary expressions (ast.IfExp)
        - Function calls (ast.Call) - whitelist only
        - Variable references (ast.Name)

        Args:
            node: AST node to evaluate.

        Returns:
            Evaluated value.

        Raises:
            ValueError: If node type is not allowed.
        """
        # === Constants ===

        # Constant (Python 3.8+)
        if isinstance(node, ast.Constant):
            return self._eval_constant(node.value)

        # Num (Python 3.7 fallback)
        if isinstance(node, ast.Num):
            return float(node.n)

        # Str (Python 3.7 fallback for string literals)
        if isinstance(node, ast.Str):
            return node.s

        # NameConstant (Python 3.7 fallback for True/False/None)
        if isinstance(node, ast.NameConstant):
            if node.value is True:
                return 1.0
            if node.value is False:
                return 0.0
            raise ValueError(f"Invalid NameConstant: {node.value}")

        # === Operations ===

        # Binary operation (+, -, *, /, //, %, **)
        if isinstance(node, ast.BinOp):
            return self._eval_binop(node)

        # Unary operation (-, +, not)
        if isinstance(node, ast.UnaryOp):
            return self._eval_unaryop(node)

        # Comparison (<, <=, >, >=, ==, !=)
        if isinstance(node, ast.Compare):
            return self._eval_compare(node)

        # Boolean operation (and, or)
        if isinstance(node, ast.BoolOp):
            return self._eval_boolop(node)

        # Ternary expression (x if cond else y)
        if isinstance(node, ast.IfExp):
            return self._eval_ifexp(node)

        # === References ===

        # Function call
        if isinstance(node, ast.Call):
            return self._eval_call(node)

        # Variable reference
        if isinstance(node, ast.Name):
            return self._eval_name(node)

        raise ValueError(f"Unsupported AST node: {type(node).__name__}")

    def _eval_constant(self, value: Any) -> Any:
        """Evaluate constant value.

        Args:
            value: Constant value from ast.Constant node.

        Returns:
            Float value (or string for string literals).

        Raises:
            ValueError: If constant type is not supported.
        """
        # CRITICAL: Check bool BEFORE int (bool is subclass of int)
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return value  # Return string for comparisons
        raise ValueError(f"Invalid constant type: {type(value).__name__}")

    def _eval_binop(self, node: ast.BinOp) -> float:
        """Evaluate binary operation.

        Args:
            node: ast.BinOp node.

        Returns:
            Result of binary operation.

        Raises:
            ValueError: If operator is not supported or operands are strings.
        """
        left = self._eval_node(node.left)
        right = self._eval_node(node.right)

        # Ensure numeric operands
        if isinstance(left, str) or isinstance(right, str):
            raise ValueError(f"Cannot perform arithmetic on strings: {left}, {right}")

        op_type = type(node.op)
        if op_type not in self.BINARY_OPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")

        return float(self.BINARY_OPS[op_type](left, right))

    def _eval_unaryop(self, node: ast.UnaryOp) -> float:
        """Evaluate unary operation.

        Args:
            node: ast.UnaryOp node.

        Returns:
            Result of unary operation.

        Raises:
            ValueError: If operator is not supported.
        """
        operand = self._eval_node(node.operand)

        if isinstance(node.op, ast.USub):
            if isinstance(operand, str):
                raise ValueError(f"Cannot negate string: {operand}")
            return -operand
        if isinstance(node.op, ast.UAdd):
            if isinstance(operand, str):
                raise ValueError(f"Cannot apply + to string: {operand}")
            return +operand
        if isinstance(node.op, ast.Not):
            # not x: return 0.0 if truthy, 1.0 if falsy
            return 0.0 if operand else 1.0

        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

    def _eval_compare(self, node: ast.Compare) -> float:
        """Evaluate comparison expression.

        Handles chained comparisons: 0 < x < 10
        Handles string comparisons: mode == 'EDIT'

        Args:
            node: ast.Compare node.

        Returns:
            1.0 if comparison is True, 0.0 if False.

        Raises:
            ValueError: If comparison operator is not supported.
        """
        left = self._eval_node(node.left)

        for op, comparator in zip(node.ops, node.comparators):
            right = self._eval_node(comparator)

            op_type = type(op)
            if op_type not in self.COMPARE_OPS:
                raise ValueError(f"Unsupported comparison operator: {op_type.__name__}")

            if not self.COMPARE_OPS[op_type](left, right):
                return 0.0  # False

            left = right  # For chained comparisons

        return 1.0  # True

    def _eval_boolop(self, node: ast.BoolOp) -> float:
        """Evaluate boolean operation with short-circuit evaluation.

        Args:
            node: ast.BoolOp node.

        Returns:
            1.0 if True, 0.0 if False.

        Raises:
            ValueError: If boolean operator is not supported.
        """
        if isinstance(node.op, ast.And):
            # All values must be truthy (non-zero, non-empty string)
            for value in node.values:
                result = self._eval_node(value)
                if not result:
                    return 0.0  # Short-circuit: first False
            return 1.0

        if isinstance(node.op, ast.Or):
            # At least one value must be truthy
            for value in node.values:
                result = self._eval_node(value)
                if result:
                    return 1.0  # Short-circuit: first True
            return 0.0

        raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")

    def _eval_ifexp(self, node: ast.IfExp) -> Any:
        """Evaluate ternary expression (x if condition else y).

        Args:
            node: ast.IfExp node.

        Returns:
            Body value if condition is truthy, else orelse value.
        """
        condition = self._eval_node(node.test)

        if condition:
            return self._eval_node(node.body)
        else:
            return self._eval_node(node.orelse)

    def _eval_call(self, node: ast.Call) -> float:
        """Evaluate function call.

        Args:
            node: ast.Call node.

        Returns:
            Function result.

        Raises:
            ValueError: If function is not in whitelist.
        """
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls allowed")

        func_name = node.func.id
        if func_name not in self.FUNCTIONS:
            raise ValueError(f"Function not allowed: {func_name}")

        args = [self._eval_node(arg) for arg in node.args]

        # Ensure all args are numeric for math functions
        for arg in args:
            if isinstance(arg, str):
                raise ValueError(
                    f"Function '{func_name}' requires numeric arguments, got string"
                )

        # Special handling for functions that need integer arguments
        if func_name == "round" and len(args) == 2:
            # round(number, ndigits) - ndigits must be int
            return float(round(args[0], int(args[1])))

        return float(self.FUNCTIONS[func_name](*args))

    def _eval_name(self, node: ast.Name) -> Any:
        """Evaluate variable reference.

        Args:
            node: ast.Name node.

        Returns:
            Variable value from context.

        Raises:
            ValueError: If variable is not in context.
        """
        var_name = node.id

        # Check context first
        if var_name in self._context:
            return self._context[var_name]

        # Handle True/False as names (Python compatibility)
        # Also handle lowercase for backward compatibility with ConditionEvaluator
        if var_name == "True" or var_name.lower() == "true":
            return 1.0
        if var_name == "False" or var_name.lower() == "false":
            return 0.0

        raise ValueError(f"Unknown variable: {var_name}")

    # === Computed Parameters (preserved from ExpressionEvaluator) ===

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
            ValueError: If circular dependency detected or evaluation fails.
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
            name: (schema.depends_on if hasattr(schema, "depends_on") and schema.depends_on else [])
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
            value = self.evaluate_safe(expr, default=None)

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

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort on dependency graph.

        TASK-056-5: Implements Kahn's algorithm for topological sorting.

        Args:
            graph: Dictionary mapping node -> list of dependencies.

        Returns:
            List of nodes in topologically sorted order.

        Raises:
            ValueError: If circular dependency detected.
        """
        # Calculate in-degrees (count only dependencies that are IN the graph)
        in_degree = {}
        for node, deps in graph.items():
            in_degree[node] = sum(1 for dep in deps if dep in graph)

        # Queue of nodes with no unmet dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        sorted_nodes = []

        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)

            for other_node in graph:
                if node in graph[other_node]:
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0:
                        queue.append(other_node)

        if len(sorted_nodes) != len(graph):
            remaining = set(graph.keys()) - set(sorted_nodes)
            raise ValueError(f"Circular dependency detected: {remaining}")

        return sorted_nodes
