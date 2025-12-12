# TASK-060: Unified Expression Evaluator

**Status**: TODO
**Priority**: P0 (Critical - Pre-launch architecture cleanup)
**Estimated Effort**: 8-10 hours
**Dependencies**: None (replaces TASK-059)
**Related**: TASK-059 (superseded), TASK-055-FIX-8 (documentation), TASK-058 (loop system)
**Created**: 2025-12-12
**Supersedes**: TASK-059 (kept as documentation reference)
**Revised**: 2025-12-12 (Clean Architecture alignment)

---

## Executive Summary

Before public launch (Blender forums, Reddit), consolidate two separate evaluators into a single, well-architected **Unified Evaluator**. This prevents technical debt and makes the system easier to extend by future contributors.

**Key Changes from Original TASK-060:**
- Added domain interface `IExpressionEvaluator` (Clean Architecture)
- Proper string/numeric type handling (Any return type, not just float)
- Preserved `simulate_step_effect()` as separate concern
- Added `resolve_computed_parameters()` to core
- Enhanced backward compatibility testing strategy

---

## Problem Statement

### Current State: Two Separate Evaluators

```
server/router/application/evaluator/
├── expression_evaluator.py   # AST-based, returns float
│   ├── Math: +, -, *, /, floor(), sin()
│   ├── Comparisons: ❌ NOT SUPPORTED
│   └── Logic: ❌ NOT SUPPORTED
│
└── condition_evaluator.py    # Regex-based, returns bool
    ├── Math: ❌ NOT SUPPORTED
    ├── Comparisons: ==, !=, <, <=, >, >=
    └── Logic: and, or, not
```

### Problems

| Issue | Impact |
|-------|--------|
| **Two parsers** | Regex parser has edge cases, AST is more robust |
| **No math in conditions** | `condition: "floor(width) > 5"` doesn't work |
| **Duplicated logic** | Comparison operators would be in two places |
| **Inconsistent behavior** | Risk of `>` working differently in each |
| **Hard to extend** | New contributors must understand two systems |
| **Maintenance burden** | Bug fixes needed in two places |

### Why Now?

- Public launch imminent (Blender forums, Reddit)
- New developers will join the project
- Technical debt is cheaper to fix now than later
- TASK-059 would add more code to the wrong architecture

---

## Solution: Unified Evaluator

### Target Architecture

```
server/router/
├── domain/
│   └── interfaces/
│       └── i_expression_evaluator.py   # NEW: Domain interface
│
└── application/
    └── evaluator/
        ├── __init__.py                  # Updated exports
        ├── unified_evaluator.py         # NEW: Core AST-based evaluator
        ├── expression_evaluator.py      # Wrapper: $CALCULATE() → float
        ├── condition_evaluator.py       # Wrapper: condition → bool
        └── proportion_resolver.py       # Unchanged
```

### Design Principles

1. **Dependency Inversion**: UnifiedEvaluator implements `IExpressionEvaluator` interface
2. **Single Source of Truth**: One AST parser for all evaluation
3. **Composition over Inheritance**: Wrappers delegate to UnifiedEvaluator
4. **Backward Compatibility**: Existing YAML workflows work unchanged
5. **Type Safety**: Core returns `Any` (float/string), wrappers enforce contracts
6. **Separation of Concerns**: `simulate_step_effect()` stays in ConditionEvaluator

---

## Requirements

### Must Have (P0)

1. **Domain Interface** `IExpressionEvaluator`:
   - Abstract contract for expression evaluation
   - Allows future alternative implementations
   - Enables dependency injection in tests

2. **UnifiedEvaluator** with full feature set:
   - All 21 math functions (from TASK-056-1)
   - All arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
   - All comparison operators: `<`, `<=`, `>`, `>=`, `==`, `!=`
   - All logical operators: `and`, `or`, `not`
   - Ternary expressions: `x if condition else y`
   - Chained comparisons: `0 < x < 10`
   - Variable references from context
   - **String comparisons**: `mode == 'EDIT'`
   - **Computed parameter resolution** with topological sort

3. **ExpressionEvaluator** wrapper:
   - `$CALCULATE(...)` pattern matching
   - `$variable` references
   - Returns `float`
   - Full backward compatibility
   - Delegates to UnifiedEvaluator

4. **ConditionEvaluator** wrapper:
   - Returns `bool`
   - Fail-open behavior (returns `True` on error)
   - Full backward compatibility with existing conditions
   - **Preserves `simulate_step_effect()`** (step context simulation)
   - Delegates to UnifiedEvaluator

5. **All existing tests pass** without modification

### Nice to Have (P1)

6. **Math in conditions**:
   ```yaml
   condition: "floor(table_width / plank_width) > 5"
   ```

7. **Consistent error messages** across both wrappers

---

## Implementation Plan

### Phase 1: Create Domain Interface

**File**: `server/router/domain/interfaces/i_expression_evaluator.py`

```python
"""
Expression Evaluator Interface.

TASK-060: Domain interface for expression evaluation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IExpressionEvaluator(ABC):
    """Abstract interface for expression evaluation.

    Defines contract for safe expression evaluation used by workflow system.
    Supports mathematical expressions, comparisons, and logical operations.

    Implementations:
        - UnifiedEvaluator: Full AST-based implementation
    """

    @abstractmethod
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dictionary with variable values.
        """
        pass

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        pass

    @abstractmethod
    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values.

        Args:
            updates: Dictionary with values to add/update.
        """
        pass

    @abstractmethod
    def get_variable(self, name: str) -> Optional[Any]:
        """Get variable value from context.

        Args:
            name: Variable name.

        Returns:
            Variable value or None if not found.
        """
        pass

    @abstractmethod
    def evaluate(self, expression: str) -> Any:
        """Evaluate expression and return result.

        Args:
            expression: Expression string to evaluate.

        Returns:
            Evaluated value (float for math, bool-as-float for comparisons).

        Raises:
            ValueError: If expression is invalid.
            SyntaxError: If expression has invalid syntax.
        """
        pass

    @abstractmethod
    def evaluate_safe(self, expression: str, default: Any = 0.0) -> Any:
        """Evaluate expression with fallback on error.

        Args:
            expression: Expression string to evaluate.
            default: Value to return on error.

        Returns:
            Evaluated value or default on error.
        """
        pass
```

**Update**: `server/router/domain/interfaces/__init__.py`

```python
# Add to existing exports:
from server.router.domain.interfaces.i_expression_evaluator import (
    IExpressionEvaluator,
)
```

---

### Phase 2: Create UnifiedEvaluator (Core Implementation)

**File**: `server/router/application/evaluator/unified_evaluator.py`

```python
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
from typing import Dict, Any, Optional, List, Union

from server.router.domain.interfaces.i_expression_evaluator import IExpressionEvaluator

logger = logging.getLogger(__name__)


class UnifiedEvaluator(IExpressionEvaluator):
    """AST-based evaluator for math, comparisons, and logic.

    Returns appropriate type based on expression:
    - Arithmetic: float
    - Comparisons: float (1.0 for True, 0.0 for False)
    - String literals: str (for string comparisons)

    Used internally by ExpressionEvaluator and ConditionEvaluator.

    Supports:
    - Arithmetic: +, -, *, /, //, %, **
    - Math functions: abs, min, max, floor, ceil, sqrt, sin, cos, etc.
    - Comparisons: <, <=, >, >=, ==, !=
    - Logic: and, or, not
    - Ternary: x if condition else y
    - Chained comparisons: 0 < x < 10
    - String comparisons: mode == 'EDIT'

    Example:
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"width": 2.0, "height": 4.0, "mode": "EDIT"})

        # Math
        evaluator.evaluate("width * 0.5")  # -> 1.0
        evaluator.evaluate("floor(height / width)")  # -> 2.0

        # Comparisons (return 1.0 for True, 0.0 for False)
        evaluator.evaluate("width > 1.0")  # -> 1.0
        evaluator.evaluate("mode == 'EDIT'")  # -> 1.0

        # Logic
        evaluator.evaluate("width > 1.0 and height < 5.0")  # -> 1.0

        # Ternary
        evaluator.evaluate("10 if width > 1.0 else 5")  # -> 10.0
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

    # Binary operators
    BINARY_OPS: Dict[type, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    # Comparison operators
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

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dictionary with variable values.
                     Supports: int, float, bool, str values.
        """
        self._context = {}

        for key, value in context.items():
            if isinstance(value, bool):
                # bool before int (bool is subclass of int)
                # Store as float for arithmetic compatibility
                self._context[key] = 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                self._context[key] = float(value)
            elif isinstance(value, str):
                # Store strings for comparison (e.g., mode == 'EDIT')
                self._context[key] = value

    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values.

        Args:
            updates: Dictionary with values to add/update.
        """
        for key, value in updates.items():
            if isinstance(value, bool):
                self._context[key] = 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                self._context[key] = float(value)
            elif isinstance(value, str):
                self._context[key] = value

    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        return dict(self._context)

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
            Evaluated value (float for math, string for string literals).

        Raises:
            ValueError: If expression is invalid or uses disallowed constructs.
            SyntaxError: If expression has invalid Python syntax.
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
        # Check bool BEFORE int (bool is subclass of int)
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
            ValueError: If operator is not supported.
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
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                raise ValueError(f"Function '{func_name}' requires numeric arguments, got string")

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
        if var_name == "True":
            return 1.0
        if var_name == "False":
            return 0.0

        raise ValueError(f"Unknown variable: {var_name}")

    # === Computed Parameters (from ExpressionEvaluator) ===

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

        Example:
            schemas = {
                "width": ParameterSchema(name="width", type="float"),
                "plank_full_count": ParameterSchema(
                    name="plank_full_count",
                    type="int",
                    computed="floor(width / plank_max_width)",
                    depends_on=["width", "plank_max_width"]
                )
            }
            context = {"width": 0.73, "plank_max_width": 0.10}
            result = evaluator.resolve_computed_parameters(schemas, context)
            # result = {"width": 0.73, "plank_max_width": 0.10, "plank_full_count": 7.0}
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
```

---

### Phase 3: Refactor ExpressionEvaluator (Wrapper)

**File**: `server/router/application/evaluator/expression_evaluator.py`

Keep the public API identical, but delegate to UnifiedEvaluator internally.

```python
"""
Expression Evaluator.

Wrapper for UnifiedEvaluator that handles $CALCULATE() expressions.
Maintains backward compatibility with existing workflow YAML files.

TASK-041-7: Original implementation
TASK-060: Refactored to use UnifiedEvaluator as core.
"""

import re
import logging
from typing import Dict, Any, Optional, List

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator

logger = logging.getLogger(__name__)


class ExpressionEvaluator:
    """Expression evaluator for $CALCULATE() and $variable references.

    This is a wrapper around UnifiedEvaluator that provides:
    - $CALCULATE(...) pattern matching
    - $variable direct references
    - Backward-compatible API

    Example:
        evaluator = ExpressionEvaluator()
        evaluator.set_context({"width": 2.0, "height": 4.0})

        result = evaluator.resolve_param_value("$CALCULATE(width * 0.5)")  # -> 1.0
        result = evaluator.resolve_param_value("$width")  # -> 2.0
        result = evaluator.resolve_param_value("$CALCULATE(1 if width > 1 else 0)")  # -> 1.0
    """

    # Pattern for $CALCULATE(...)
    CALCULATE_PATTERN = re.compile(r"^\$CALCULATE\((.+)\)$")

    # Pattern for simple $variable reference
    VARIABLE_PATTERN = re.compile(r"^\$([a-zA-Z_][a-zA-Z0-9_]*)$")

    # Expose FUNCTIONS for backward compatibility
    FUNCTIONS = UnifiedEvaluator.FUNCTIONS

    def __init__(self):
        """Initialize expression evaluator."""
        self._unified = UnifiedEvaluator()

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dict with variable values.

        Handles special keys:
            - dimensions: List[float] of [x, y, z] -> extracts width/height/depth
            - proportions: Dict -> flattens to proportions_* keys
        """
        flat_context = {}

        # Extract dimensions
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

        # Pass through all other values
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
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        return self._unified.get_context()

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

        TASK-056-5: Delegates to UnifiedEvaluator.resolve_computed_parameters().

        Args:
            schemas: Dictionary of parameter name -> ParameterSchema.
            context: Initial parameter values (non-computed parameters).

        Returns:
            Dictionary with all parameters (non-computed + computed).

        Raises:
            ValueError: If circular dependency detected or unknown variable.
        """
        return self._unified.resolve_computed_parameters(schemas, context)
```

---

### Phase 4: Refactor ConditionEvaluator (Wrapper)

**File**: `server/router/application/evaluator/condition_evaluator.py`

```python
"""
Condition Evaluator.

Wrapper for UnifiedEvaluator that evaluates boolean conditions for workflow steps.
Maintains backward compatibility with existing workflow YAML files.

TASK-041-10: Original implementation
TASK-060: Refactored to use UnifiedEvaluator as core.
"""

import logging
from typing import Dict, Any

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates boolean conditions for workflow step execution.

    This is a wrapper around UnifiedEvaluator that provides:
    - Boolean return type (converts float to bool)
    - Fail-open behavior (returns True on error)
    - Backward-compatible API
    - Step effect simulation (simulate_step_effect)

    Supported conditions:
    - Comparisons: "width > 1.0", "mode == 'EDIT'", "count != 0"
    - Logic: "width > 1.0 and height < 2.0", "not has_selection"
    - Math in conditions: "floor(width / 0.1) > 5" (NEW in TASK-060)
    - Ternary: "1 if is_large else 0"

    Example:
        evaluator = ConditionEvaluator()
        evaluator.set_context({"mode": "OBJECT", "width": 1.5})

        evaluator.evaluate("mode == 'OBJECT'")  # -> True
        evaluator.evaluate("width > 1.0")  # -> True
        evaluator.evaluate("width > 1.0 and mode == 'EDIT'")  # -> False
        evaluator.evaluate("floor(width) > 0")  # -> True (NEW)
    """

    def __init__(self):
        """Initialize condition evaluator."""
        self._unified = UnifiedEvaluator()

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set evaluation context.

        Args:
            context: Dictionary with variable values.
        """
        self._unified.set_context(context)

    def set_context_from_scene(self, scene_context: Any) -> None:
        """Set context from SceneContext object.

        Args:
            scene_context: SceneContext instance.
        """
        context = {
            "current_mode": scene_context.mode,
            "has_selection": scene_context.has_selection,
            "object_count": len(scene_context.objects) if scene_context.objects else 0,
            "active_object": scene_context.active_object,
        }

        if scene_context.topology:
            context["selected_verts"] = scene_context.topology.selected_verts
            context["selected_edges"] = scene_context.topology.selected_edges
            context["selected_faces"] = scene_context.topology.selected_faces
            context["total_verts"] = scene_context.topology.total_verts
            context["total_edges"] = scene_context.topology.total_edges
            context["total_faces"] = scene_context.topology.total_faces

        self._unified.set_context(context)

    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        return self._unified.get_context()

    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values.

        Args:
            updates: Dictionary with values to update.
        """
        self._unified.update_context(updates)

    def evaluate(self, condition: str) -> bool:
        """Evaluate a condition string.

        Args:
            condition: Condition expression.

        Returns:
            True if condition is met, False otherwise.
            Returns True if condition is empty or invalid (fail-open).
        """
        if not condition or not condition.strip():
            return True

        condition = condition.strip()

        try:
            logger.debug(
                f"Evaluating condition '{condition}' with context keys: "
                f"{list(self._unified.get_context().keys())}"
            )

            result = self._unified.evaluate_as_bool(condition)

            logger.debug(f"Condition '{condition}' evaluated to {result}")
            return result

        except Exception as e:
            logger.warning(f"Condition evaluation failed: '{condition}' - {e}")
            return True  # Fail-open

    def simulate_step_effect(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Simulate the effect of a workflow step on context.

        Updates the context to reflect what would happen after
        executing a tool. Used for conditional step evaluation.

        This method is NOT delegated to UnifiedEvaluator because it's
        workflow-specific logic, not expression evaluation logic.

        Args:
            tool_name: Name of the tool being executed.
            params: Tool parameters.
        """
        updates = {}

        if tool_name in ("system_set_mode", "scene_set_mode"):
            mode = params.get("mode")
            if mode:
                updates["current_mode"] = mode

        elif tool_name == "mesh_select":
            action = params.get("action")
            if action == "all":
                updates["has_selection"] = True
            elif action == "none":
                updates["has_selection"] = False

        elif tool_name == "mesh_select_targeted":
            updates["has_selection"] = True

        elif tool_name == "modeling_create_primitive":
            current = self._unified.get_context().get("object_count", 0)
            updates["object_count"] = current + 1

        elif tool_name == "scene_delete_object":
            current = self._unified.get_context().get("object_count", 0)
            if current > 0:
                updates["object_count"] = current - 1

        if updates:
            self._unified.update_context(updates)
```

---

### Phase 5: Update `__init__.py`

**File**: `server/router/application/evaluator/__init__.py`

```python
"""
Evaluator Module.

Contains expression, condition, and proportion evaluators for workflow parameter resolution.

TASK-041-7: ExpressionEvaluator for $CALCULATE(...) expressions
TASK-041-10: ConditionEvaluator for conditional step execution
TASK-041-13: ProportionResolver for $AUTO_* parameters
TASK-060: UnifiedEvaluator as core implementation
"""

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator
from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator
from server.router.application.evaluator.condition_evaluator import ConditionEvaluator
from server.router.application.evaluator.proportion_resolver import ProportionResolver

__all__ = [
    "UnifiedEvaluator",
    "ExpressionEvaluator",
    "ConditionEvaluator",
    "ProportionResolver",
]
```

---

## Test Strategy

### Phase 6: Unit Tests for UnifiedEvaluator

**File**: `tests/unit/router/application/evaluator/test_unified_evaluator.py`

Create comprehensive tests covering:

1. **Arithmetic Operations**
   - All operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
   - Operator precedence
   - Parentheses grouping

2. **Math Functions**
   - All 21 functions from TASK-056-1
   - Nested function calls
   - Error handling for invalid arguments

3. **Comparison Operators**
   - All operators: `<`, `<=`, `>`, `>=`, `==`, `!=`
   - Chained comparisons: `0 < x < 10`
   - String comparisons: `mode == 'EDIT'`
   - Mixed type comparisons (error cases)

4. **Logical Operators**
   - `and`, `or`, `not`
   - Operator precedence: `not` > `and` > `or`
   - Short-circuit evaluation
   - Combined with comparisons

5. **Ternary Expressions**
   - Simple ternary: `x if cond else y`
   - Nested ternary
   - With comparisons and logic

6. **Boolean Literals**
   - `True`, `False` as literals
   - Boolean in arithmetic context
   - `not True`, `not False`

7. **Context Management**
   - `set_context()` with various types
   - `update_context()` merging
   - `get_variable()` retrieval
   - Unknown variable handling

8. **Computed Parameters**
   - `resolve_computed_parameters()` with dependencies
   - Topological sort
   - Circular dependency detection

9. **Error Handling**
   - Empty expressions
   - Syntax errors
   - Unknown variables
   - Disallowed functions
   - Type errors (string in arithmetic)

10. **Security**
    - No imports
    - No eval/exec
    - No attribute access
    - No subscript access

### Phase 7: Backward Compatibility Tests

**CRITICAL**: All existing tests MUST pass without modification:

- `tests/unit/router/application/evaluator/test_expression_evaluator.py`
- `tests/unit/router/application/evaluator/test_expression_evaluator_extended.py`
- `tests/unit/router/application/evaluator/test_condition_evaluator.py`
- `tests/unit/router/application/evaluator/test_condition_evaluator_parentheses.py`

### Phase 8: Integration Tests

**File**: `tests/unit/router/application/evaluator/test_unified_integration.py`

Test integration with:
- WorkflowRegistry parameter resolution
- Condition evaluation in workflow steps
- Computed parameters in real workflows

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `server/router/domain/interfaces/i_expression_evaluator.py` | **CREATE** | Domain interface |
| `server/router/domain/interfaces/__init__.py` | **MODIFY** | Export interface |
| `server/router/application/evaluator/unified_evaluator.py` | **CREATE** | Core AST-based evaluator |
| `server/router/application/evaluator/expression_evaluator.py` | **MODIFY** | Refactor to use UnifiedEvaluator |
| `server/router/application/evaluator/condition_evaluator.py` | **MODIFY** | Refactor to use UnifiedEvaluator |
| `server/router/application/evaluator/__init__.py` | **MODIFY** | Export UnifiedEvaluator |
| `tests/unit/router/application/evaluator/test_unified_evaluator.py` | **CREATE** | Core tests |
| `tests/unit/router/application/evaluator/test_unified_integration.py` | **CREATE** | Integration tests |

---

## Migration Checklist

### Before Implementation
- [ ] Read existing `expression_evaluator.py` thoroughly
- [ ] Read existing `condition_evaluator.py` thoroughly
- [ ] Run all existing tests, ensure they pass
- [ ] Create snapshot of test results

### Implementation
- [ ] Phase 1: Create `i_expression_evaluator.py` interface
- [ ] Phase 2: Create `unified_evaluator.py`
- [ ] Phase 3: Refactor `expression_evaluator.py`
- [ ] Phase 4: Refactor `condition_evaluator.py`
- [ ] Phase 5: Update `__init__.py`
- [ ] Phase 6: Write `test_unified_evaluator.py`
- [ ] Phase 7: Verify all existing tests pass
- [ ] Phase 8: Write integration tests

### Verification
- [ ] All existing tests pass (backward compatibility)
- [ ] All new tests pass
- [ ] Manual test with real workflow YAML
- [ ] Test math in conditions: `condition: "floor(width) > 5"`
- [ ] Test string comparisons: `condition: "mode == 'EDIT'"`
- [ ] Test ternary in $CALCULATE: `$CALCULATE(x if y > 0 else z)`

### Documentation
- [ ] Update TASK-059 status to "Superseded by TASK-060"
- [ ] Update TASK-055-FIX-8 with new capabilities
- [ ] Create changelog entry
- [ ] Update `_docs/_ROUTER/IMPLEMENTATION/25-expression-evaluator.md`
- [ ] Update `_docs/_ROUTER/IMPLEMENTATION/26-condition-evaluator.md`

---

## Acceptance Criteria

### Must Pass
- [ ] Domain interface `IExpressionEvaluator` exists
- [ ] UnifiedEvaluator implements interface
- [ ] All 21 math functions work
- [ ] All arithmetic operators work: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- [ ] All comparison operators work: `<`, `<=`, `>`, `>=`, `==`, `!=`
- [ ] All logical operators work: `and`, `or`, `not`
- [ ] Ternary expressions work: `x if condition else y`
- [ ] Chained comparisons work: `0 < x < 10`
- [ ] String comparisons work: `mode == 'EDIT'`
- [ ] `$CALCULATE()` pattern still works
- [ ] `$variable` pattern still works
- [ ] Condition fail-open behavior preserved
- [ ] `simulate_step_effect()` preserved
- [ ] `resolve_computed_parameters()` works
- [ ] All existing tests pass unchanged

### New Capabilities
- [ ] Math functions work in conditions: `floor(width) > 5`
- [ ] `evaluate_safe()` method available
- [ ] `evaluate_as_bool()` method available
- [ ] `evaluate_as_float()` method available

---

## Rollback Plan

If issues arise after deployment:

1. Revert to previous `expression_evaluator.py` and `condition_evaluator.py`
2. Remove `unified_evaluator.py`
3. Remove `i_expression_evaluator.py`
4. Revert `__init__.py`

The old code is self-contained, so rollback is straightforward.

---

## Architectural Decisions

### Why Domain Interface?

1. **Clean Architecture Compliance**: All major router components have domain interfaces
2. **Testability**: Allows mocking evaluator in unit tests
3. **Future Extensions**: Could have alternative implementations (e.g., cached evaluator)
4. **Dependency Inversion**: High-level modules don't depend on concrete implementation

### Why `Any` Return Type in Core?

1. **String Comparisons**: Need to return strings for `mode == 'EDIT'` to work
2. **Type Safety at Wrapper Level**: ExpressionEvaluator enforces float, ConditionEvaluator enforces bool
3. **Flexibility**: Ternary expressions can return different types in different branches

### Why Keep `simulate_step_effect()` in ConditionEvaluator?

1. **Separation of Concerns**: Step simulation is workflow logic, not expression evaluation
2. **Single Responsibility**: UnifiedEvaluator handles math/logic, not workflow state
3. **Backward Compatibility**: No changes needed to WorkflowRegistry

### Why Topological Sort in UnifiedEvaluator?

1. **Computed Parameters**: Required for $CALCULATE dependencies
2. **Code Reuse**: Both ExpressionEvaluator and potential future uses benefit
3. **Centralized Logic**: Algorithm in one place, not duplicated

---

## Notes

- TASK-059 remains as documentation reference for the logical operators implementation details
- UnifiedEvaluator returns `Any` (float or string); wrappers enforce type contracts
- `bool` is checked before `int` in `_eval_constant()` (bool is subclass of int)
- Python 3.7 compatibility maintained via `ast.Num`, `ast.Str`, `ast.NameConstant`
- Security maintained via AST node whitelist (no eval, exec, imports)
- `simulate_step_effect()` stays in ConditionEvaluator (workflow-specific logic)

---

## Related Tasks

- **TASK-059**: Superseded - kept as implementation reference
- **TASK-055-FIX-8**: Documentation to update after completion
- **TASK-056-1**: Extended math functions (already in FUNCTIONS dict)
- **TASK-056-5**: Computed parameter dependencies (integrated into UnifiedEvaluator)
- **TASK-058**: Loop system (will benefit from ternary support)

---

## Post-Implementation

After TASK-060 is complete:

1. Update TASK-059 header:
   ```markdown
   **Status**: ⚠️ SUPERSEDED by TASK-060
   ```

2. Update TASK-055-FIX-8:
   - Mark comparison operators as ✅
   - Mark logical operators as ✅
   - Mark ternary expressions as ✅
   - Add note about math in conditions

3. Create changelog:
   ```markdown
   # 2025-12-XX: Unified Expression Evaluator (TASK-060)

   ## Added
   - `IExpressionEvaluator` domain interface (Clean Architecture)
   - `UnifiedEvaluator` as single source of truth for expression evaluation
   - Comparison operators in $CALCULATE: <, <=, >, >=, ==, !=
   - Logical operators in $CALCULATE: and, or, not
   - Ternary expressions: x if condition else y
   - Chained comparisons: 0 < x < 10
   - Math functions in workflow conditions

   ## Changed
   - ExpressionEvaluator now delegates to UnifiedEvaluator
   - ConditionEvaluator now delegates to UnifiedEvaluator

   ## Preserved
   - Full backward compatibility with existing workflows
   - simulate_step_effect() for workflow state simulation
   - Fail-open behavior in ConditionEvaluator
   ```

4. Update Router documentation:
   - `_docs/_ROUTER/IMPLEMENTATION/25-expression-evaluator.md`
   - `_docs/_ROUTER/IMPLEMENTATION/26-condition-evaluator.md`
   - Add new doc: `_docs/_ROUTER/IMPLEMENTATION/XX-unified-evaluator.md`
