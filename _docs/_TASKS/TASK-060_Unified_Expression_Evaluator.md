# TASK-060: Unified Expression Evaluator

**Status**: TODO
**Priority**: P0 (Critical - Pre-launch architecture cleanup)
**Estimated Effort**: 6-8 hours
**Dependencies**: None (replaces TASK-059)
**Related**: TASK-059 (superseded), TASK-055-FIX-8 (documentation), TASK-058 (loop system)
**Created**: 2025-12-12
**Supersedes**: TASK-059 (kept as documentation reference)

---

## Executive Summary

Before public launch (Blender forums, Reddit), consolidate two separate evaluators into a single, well-architected **Unified Evaluator**. This prevents technical debt and makes the system easier to extend by future contributors.

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
server/router/application/evaluator/
├── __init__.py
├── unified_evaluator.py      # NEW: Core AST-based evaluator
├── expression_evaluator.py   # Wrapper: $CALCULATE() → float
├── condition_evaluator.py    # Wrapper: condition → bool (backward compat)
├── proportion_resolver.py    # Unchanged
└── (legacy code removed)
```

### Design Principles

1. **Single Source of Truth**: One AST parser for all evaluation
2. **Composition over Inheritance**: Wrappers delegate to UnifiedEvaluator
3. **Backward Compatibility**: Existing YAML workflows work unchanged
4. **Type Safety**: Clear contracts (float vs bool) at wrapper level
5. **Extensibility**: Add function once, available everywhere

---

## Requirements

### Must Have (P0)

1. **UnifiedEvaluator** with full feature set:
   - All 21 math functions (from TASK-056-1)
   - All arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
   - All comparison operators: `<`, `<=`, `>`, `>=`, `==`, `!=`
   - All logical operators: `and`, `or`, `not`
   - Ternary expressions: `x if condition else y`
   - Chained comparisons: `0 < x < 10`
   - Variable references from context

2. **ExpressionEvaluator** wrapper:
   - `$CALCULATE(...)` pattern matching
   - `$variable` references
   - Returns `float`
   - Full backward compatibility

3. **ConditionEvaluator** wrapper:
   - Returns `bool`
   - Fail-open behavior (returns `True` on error)
   - Full backward compatibility with existing conditions

4. **All existing tests pass** without modification

### Nice to Have (P1)

5. **Math in conditions**:
   ```yaml
   condition: "floor(table_width / plank_width) > 5"
   ```

6. **Consistent error messages** across both wrappers

---

## Implementation Plan

### Phase 1: Create UnifiedEvaluator (Core)

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
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class UnifiedEvaluator:
    """AST-based evaluator for math, comparisons, and logic.

    Returns float for all operations (bool represented as 1.0/0.0).
    Used internally by ExpressionEvaluator and ConditionEvaluator.

    Supports:
    - Arithmetic: +, -, *, /, //, %, **
    - Math functions: abs, min, max, floor, ceil, sqrt, sin, cos, etc.
    - Comparisons: <, <=, >, >=, ==, !=
    - Logic: and, or, not
    - Ternary: x if condition else y
    - Chained comparisons: 0 < x < 10

    Example:
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"width": 2.0, "height": 4.0})

        # Math
        evaluator.evaluate("width * 0.5")  # -> 1.0
        evaluator.evaluate("floor(height / width)")  # -> 2.0

        # Comparisons (return 1.0 for True, 0.0 for False)
        evaluator.evaluate("width > 1.0")  # -> 1.0
        evaluator.evaluate("width > 5.0")  # -> 0.0

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
        self._context: Dict[str, float] = {}

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dictionary with variable values.
                     Non-numeric values are converted or skipped.
        """
        self._context = {}

        for key, value in context.items():
            if isinstance(value, bool):
                # bool before int (bool is subclass of int)
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

    def evaluate(self, expression: str) -> float:
        """Evaluate expression and return float result.

        Args:
            expression: Expression string to evaluate.

        Returns:
            Evaluated float value.

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

    def evaluate_safe(self, expression: str, default: float = 0.0) -> float:
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

    def _eval_node(self, node: ast.AST) -> float:
        """Recursively evaluate AST node.

        Args:
            node: AST node to evaluate.

        Returns:
            Evaluated float value.

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
            return node.s  # Return string for comparisons

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
            return -operand
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.Not):
            return 0.0 if operand else 1.0

        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

    def _eval_compare(self, node: ast.Compare) -> float:
        """Evaluate comparison expression.

        Handles chained comparisons: 0 < x < 10

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
            # All values must be truthy (non-zero)
            for value in node.values:
                if not self._eval_node(value):
                    return 0.0  # Short-circuit: first False
            return 1.0

        if isinstance(node.op, ast.Or):
            # At least one value must be truthy
            for value in node.values:
                if self._eval_node(value):
                    return 1.0  # Short-circuit: first True
            return 0.0

        raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")

    def _eval_ifexp(self, node: ast.IfExp) -> float:
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
```

---

### Phase 2: Refactor ExpressionEvaluator (Wrapper)

**File**: `server/router/application/evaluator/expression_evaluator.py`

Keep the public API identical, but delegate to UnifiedEvaluator internally.

```python
"""
Expression Evaluator.

Wrapper for UnifiedEvaluator that handles $CALCULATE() expressions.
Maintains backward compatibility with existing workflow YAML files.

TASK-060: Refactored to use UnifiedEvaluator as core.
"""

import re
import logging
from typing import Dict, Any, Optional, List

from .unified_evaluator import UnifiedEvaluator

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

        # Pass through all other numeric values
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
            result = self._unified.evaluate(expression)
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

        Args:
            schemas: Dictionary of parameter name -> ParameterSchema.
            context: Initial parameter values.

        Returns:
            Dictionary with all parameters resolved.

        Raises:
            ValueError: If circular dependency or evaluation fails.
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
            self.set_context(resolved)

            expr = schema.computed
            value = self.evaluate(expr)

            if value is None:
                raise ValueError(
                    f"Failed to compute parameter '{param_name}' "
                    f"with expression: {expr}"
                )

            resolved[param_name] = value
            logger.debug(f"Computed parameter '{param_name}' = {value}")

        return resolved

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Topological sort using Kahn's algorithm.

        Args:
            graph: Dict mapping node -> list of dependencies.

        Returns:
            Sorted list of nodes.

        Raises:
            ValueError: If circular dependency detected.
        """
        in_degree = {}
        for node, deps in graph.items():
            in_degree[node] = sum(1 for dep in deps if dep in graph)

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

### Phase 3: Refactor ConditionEvaluator (Wrapper)

**File**: `server/router/application/evaluator/condition_evaluator.py`

```python
"""
Condition Evaluator.

Wrapper for UnifiedEvaluator that evaluates boolean conditions for workflow steps.
Maintains backward compatibility with existing workflow YAML files.

TASK-060: Refactored to use UnifiedEvaluator as core.
"""

import logging
from typing import Dict, Any

from .unified_evaluator import UnifiedEvaluator

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates boolean conditions for workflow step execution.

    This is a wrapper around UnifiedEvaluator that provides:
    - Boolean return type (converts float to bool)
    - Fail-open behavior (returns True on error)
    - Backward-compatible API

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

            # Handle string comparisons with quotes
            # UnifiedEvaluator needs 'EDIT' not EDIT for strings
            processed = self._preprocess_condition(condition)

            result = self._unified.evaluate(processed)
            bool_result = bool(result)

            logger.debug(f"Condition '{condition}' evaluated to {bool_result}")
            return bool_result

        except Exception as e:
            logger.warning(f"Condition evaluation failed: '{condition}' - {e}")
            return True  # Fail-open

    def _preprocess_condition(self, condition: str) -> str:
        """Preprocess condition for UnifiedEvaluator compatibility.

        Handles edge cases like unquoted string literals in legacy conditions.

        Args:
            condition: Original condition string.

        Returns:
            Preprocessed condition string.
        """
        # For now, pass through as-is
        # The UnifiedEvaluator handles quoted strings natively
        return condition

    def simulate_step_effect(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Simulate the effect of a workflow step on context.

        Updates the context to reflect what would happen after
        executing a tool. Used for conditional step evaluation.

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

### Phase 4: Update `__init__.py`

**File**: `server/router/application/evaluator/__init__.py`

```python
"""
Evaluator module.

Provides expression and condition evaluation for workflow parameters.

TASK-060: Unified architecture with single AST-based core.
"""

from .unified_evaluator import UnifiedEvaluator
from .expression_evaluator import ExpressionEvaluator
from .condition_evaluator import ConditionEvaluator
from .proportion_resolver import ProportionResolver

__all__ = [
    "UnifiedEvaluator",
    "ExpressionEvaluator",
    "ConditionEvaluator",
    "ProportionResolver",
]
```

---

## Test Strategy

### Phase 5: Unit Tests for UnifiedEvaluator

**File**: `tests/unit/router/application/evaluator/test_unified_evaluator.py`

```python
"""
Unit tests for UnifiedEvaluator.

TASK-060: Core evaluator tests covering all features.
"""

import pytest
import math
from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator


class TestUnifiedEvaluatorInit:
    """Test evaluator initialization."""

    def test_init_empty_context(self):
        evaluator = UnifiedEvaluator()
        assert evaluator.get_context() == {}

    def test_set_context_numeric(self):
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"width": 2.0, "height": 4, "depth": 0.5})

        context = evaluator.get_context()
        assert context["width"] == 2.0
        assert context["height"] == 4.0
        assert context["depth"] == 0.5

    def test_set_context_bool_conversion(self):
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"is_large": True, "is_small": False})

        context = evaluator.get_context()
        assert context["is_large"] == 1.0
        assert context["is_small"] == 0.0

    def test_set_context_string(self):
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"mode": "EDIT"})

        assert evaluator.get_context()["mode"] == "EDIT"


class TestArithmeticOperations:
    """Test arithmetic operations."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
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
        assert evaluator.evaluate("width * height") == 8.0

    def test_division(self, evaluator):
        assert evaluator.evaluate("10 / 2") == 5.0
        assert evaluator.evaluate("height / width") == 2.0

    def test_floor_division(self, evaluator):
        assert evaluator.evaluate("10 // 3") == 3.0
        assert evaluator.evaluate("7 // 2") == 3.0

    def test_modulo(self, evaluator):
        assert evaluator.evaluate("10 % 3") == 1.0

    def test_power(self, evaluator):
        assert evaluator.evaluate("2 ** 3") == 8.0
        assert evaluator.evaluate("width ** 2") == 4.0

    def test_unary_minus(self, evaluator):
        assert evaluator.evaluate("-5") == -5.0
        assert evaluator.evaluate("-width") == -2.0

    def test_unary_plus(self, evaluator):
        assert evaluator.evaluate("+5") == 5.0


class TestMathFunctions:
    """Test math function support."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"x": 4.0, "angle": 0.0})
        return e

    def test_abs(self, evaluator):
        assert evaluator.evaluate("abs(-5)") == 5.0

    def test_min_max(self, evaluator):
        assert evaluator.evaluate("min(3, 5)") == 3.0
        assert evaluator.evaluate("max(3, 5)") == 5.0

    def test_floor_ceil(self, evaluator):
        assert evaluator.evaluate("floor(3.7)") == 3.0
        assert evaluator.evaluate("ceil(3.2)") == 4.0

    def test_sqrt(self, evaluator):
        assert evaluator.evaluate("sqrt(x)") == 2.0

    def test_trig(self, evaluator):
        assert evaluator.evaluate("sin(angle)") == pytest.approx(0.0)
        assert evaluator.evaluate("cos(angle)") == pytest.approx(1.0)

    def test_nested_functions(self, evaluator):
        assert evaluator.evaluate("min(abs(-5), max(2, 3))") == 3.0


class TestComparisonOperators:
    """Test comparison operators."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"width": 1.5, "height": 0.8, "count": 5})
        return e

    def test_less_than(self, evaluator):
        assert evaluator.evaluate("width < 2.0") == 1.0
        assert evaluator.evaluate("width < 1.0") == 0.0

    def test_less_than_equal(self, evaluator):
        assert evaluator.evaluate("width <= 1.5") == 1.0
        assert evaluator.evaluate("width <= 1.0") == 0.0

    def test_greater_than(self, evaluator):
        assert evaluator.evaluate("width > 1.0") == 1.0
        assert evaluator.evaluate("width > 2.0") == 0.0

    def test_greater_than_equal(self, evaluator):
        assert evaluator.evaluate("height >= 0.8") == 1.0
        assert evaluator.evaluate("height >= 1.0") == 0.0

    def test_equal(self, evaluator):
        assert evaluator.evaluate("count == 5") == 1.0
        assert evaluator.evaluate("count == 3") == 0.0

    def test_not_equal(self, evaluator):
        assert evaluator.evaluate("count != 3") == 1.0
        assert evaluator.evaluate("count != 5") == 0.0

    def test_chained_comparison(self, evaluator):
        assert evaluator.evaluate("1.0 < width < 2.0") == 1.0
        assert evaluator.evaluate("0.0 < width < 1.0") == 0.0
        assert evaluator.evaluate("0 < count < 10") == 1.0

    def test_string_comparison(self, evaluator):
        evaluator.set_context({"mode": "EDIT"})
        assert evaluator.evaluate("mode == 'EDIT'") == 1.0
        assert evaluator.evaluate("mode == 'OBJECT'") == 0.0
        assert evaluator.evaluate("mode != 'OBJECT'") == 1.0


class TestLogicalOperators:
    """Test logical operators (and, or, not)."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({"a": 1.0, "b": 0.0, "c": 1.0, "width": 1.5})
        return e

    def test_and_both_true(self, evaluator):
        assert evaluator.evaluate("a and c") == 1.0

    def test_and_one_false(self, evaluator):
        assert evaluator.evaluate("a and b") == 0.0

    def test_and_with_comparisons(self, evaluator):
        assert evaluator.evaluate("width > 1.0 and width < 2.0") == 1.0

    def test_or_both_true(self, evaluator):
        assert evaluator.evaluate("a or c") == 1.0

    def test_or_one_true(self, evaluator):
        assert evaluator.evaluate("a or b") == 1.0

    def test_or_both_false(self, evaluator):
        assert evaluator.evaluate("b or 0") == 0.0

    def test_not_true(self, evaluator):
        assert evaluator.evaluate("not a") == 0.0

    def test_not_false(self, evaluator):
        assert evaluator.evaluate("not b") == 1.0

    def test_precedence_and_or(self, evaluator):
        # a and b or c = (a and b) or c = (1 and 0) or 1 = 0 or 1 = 1
        assert evaluator.evaluate("a and b or c") == 1.0

    def test_precedence_or_and(self, evaluator):
        # b or a and c = b or (a and c) = 0 or (1 and 1) = 0 or 1 = 1
        assert evaluator.evaluate("b or a and c") == 1.0


class TestTernaryExpressions:
    """Test ternary if...else expressions."""

    @pytest.fixture
    def evaluator(self):
        e = UnifiedEvaluator()
        e.set_context({
            "width": 1.5,
            "plank_full_count": 7,
            "plank_max_width": 0.10,
            "plank_remainder_width": 0.03,
            "i": 5
        })
        return e

    def test_ternary_true_branch(self, evaluator):
        assert evaluator.evaluate("10 if width > 1.0 else 5") == 10.0

    def test_ternary_false_branch(self, evaluator):
        assert evaluator.evaluate("10 if width < 1.0 else 5") == 5.0

    def test_ternary_with_variables(self, evaluator):
        result = evaluator.evaluate(
            "plank_max_width if i <= plank_full_count else plank_remainder_width"
        )
        assert result == 0.10

    def test_ternary_nested(self, evaluator):
        result = evaluator.evaluate(
            "0.05 if width < 1.0 else (0.10 if width < 2.0 else 0.15)"
        )
        assert result == 0.10

    def test_boolean_to_int_pattern(self, evaluator):
        result = evaluator.evaluate("1 if plank_remainder_width > 0.01 else 0")
        assert result == 1.0


class TestBooleanLiterals:
    """Test True/False literal handling."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_true_literal(self, evaluator):
        assert evaluator.evaluate("True") == 1.0
        assert evaluator.evaluate("1 if True else 0") == 1.0

    def test_false_literal(self, evaluator):
        assert evaluator.evaluate("False") == 0.0
        assert evaluator.evaluate("1 if False else 0") == 0.0

    def test_true_in_arithmetic(self, evaluator):
        assert evaluator.evaluate("True + 1") == 2.0
        assert evaluator.evaluate("False + 1") == 1.0

    def test_not_true_false(self, evaluator):
        assert evaluator.evaluate("not True") == 0.0
        assert evaluator.evaluate("not False") == 1.0


class TestRealWorldScenarios:
    """Tests based on real workflow use cases."""

    def test_plank_calculation(self):
        """Real example from simple_table.yaml"""
        evaluator = UnifiedEvaluator()
        evaluator.set_context({
            "table_width": 0.73,
            "plank_max_width": 0.10,
        })

        # Calculate full plank count
        result = evaluator.evaluate("floor(table_width / plank_max_width)")
        assert result == 7.0

        # Update context with computed value
        evaluator.update_context({"plank_full_count": 7})

        # Calculate remainder
        result = evaluator.evaluate("table_width - (plank_full_count * plank_max_width)")
        assert result == pytest.approx(0.03)

        # Check if remainder exists
        evaluator.update_context({"plank_remainder_width": 0.03})
        result = evaluator.evaluate("1 if plank_remainder_width > 0.01 else 0")
        assert result == 1.0

    def test_conditional_plank_width(self):
        """Select plank width based on index"""
        evaluator = UnifiedEvaluator()
        evaluator.set_context({
            "plank_full_count": 7,
            "plank_max_width": 0.10,
            "plank_remainder_width": 0.03,
            "i": 5
        })

        # Index within full planks
        result = evaluator.evaluate(
            "plank_max_width if i <= plank_full_count else plank_remainder_width"
        )
        assert result == 0.10

        # Index beyond full planks
        evaluator.update_context({"i": 8})
        result = evaluator.evaluate(
            "plank_max_width if i <= plank_full_count else plank_remainder_width"
        )
        assert result == 0.03

    def test_math_in_condition(self):
        """Math functions in boolean context (NEW in TASK-060)"""
        evaluator = UnifiedEvaluator()
        evaluator.set_context({"table_width": 0.73, "plank_width": 0.10})

        # This didn't work in old ConditionEvaluator
        result = evaluator.evaluate("floor(table_width / plank_width) > 5")
        assert result == 1.0  # floor(7.3) = 7 > 5


class TestErrorHandling:
    """Test error cases."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_empty_expression(self, evaluator):
        with pytest.raises(ValueError, match="Empty expression"):
            evaluator.evaluate("")

    def test_syntax_error(self, evaluator):
        with pytest.raises(ValueError, match="Invalid expression syntax"):
            evaluator.evaluate("2 +")

    def test_unknown_variable(self, evaluator):
        with pytest.raises(ValueError, match="Unknown variable"):
            evaluator.evaluate("unknown_var * 2")

    def test_unknown_function(self, evaluator):
        with pytest.raises(ValueError, match="Function not allowed"):
            evaluator.evaluate("eval('1+1')")

    def test_evaluate_safe_returns_default(self, evaluator):
        result = evaluator.evaluate_safe("invalid syntax +++", default=42.0)
        assert result == 42.0

    def test_division_by_zero(self, evaluator):
        with pytest.raises(ZeroDivisionError):
            evaluator.evaluate("1 / 0")


class TestSecurity:
    """Test that dangerous operations are blocked."""

    @pytest.fixture
    def evaluator(self):
        return UnifiedEvaluator()

    def test_no_imports(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("__import__('os')")

    def test_no_eval(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("eval('1+1')")

    def test_no_exec(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("exec('x=1')")

    def test_no_attribute_access(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("'string'.upper()")

    def test_no_subscript(self, evaluator):
        with pytest.raises(ValueError):
            evaluator.evaluate("[1,2,3][0]")
```

### Phase 6: Ensure Backward Compatibility Tests Pass

All existing tests in:
- `tests/unit/router/application/evaluator/test_expression_evaluator.py`
- `tests/unit/router/application/evaluator/test_expression_evaluator_extended.py`
- `tests/unit/router/application/evaluator/test_condition_evaluator.py`
- `tests/unit/router/application/evaluator/test_condition_evaluator_parentheses.py`

**MUST pass without modification.** This validates backward compatibility.

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `server/router/application/evaluator/unified_evaluator.py` | **CREATE** | Core AST-based evaluator |
| `server/router/application/evaluator/expression_evaluator.py` | **MODIFY** | Refactor to use UnifiedEvaluator |
| `server/router/application/evaluator/condition_evaluator.py` | **MODIFY** | Refactor to use UnifiedEvaluator |
| `server/router/application/evaluator/__init__.py` | **MODIFY** | Export UnifiedEvaluator |
| `tests/unit/router/application/evaluator/test_unified_evaluator.py` | **CREATE** | Core tests |

---

## Migration Checklist

### Before Implementation
- [ ] Read existing `expression_evaluator.py` thoroughly
- [ ] Read existing `condition_evaluator.py` thoroughly
- [ ] Run all existing tests, ensure they pass
- [ ] Create snapshot of test results

### Implementation
- [ ] Phase 1: Create `unified_evaluator.py`
- [ ] Phase 2: Refactor `expression_evaluator.py`
- [ ] Phase 3: Refactor `condition_evaluator.py`
- [ ] Phase 4: Update `__init__.py`
- [ ] Phase 5: Write `test_unified_evaluator.py`

### Verification
- [ ] All existing tests pass (backward compatibility)
- [ ] All new tests pass
- [ ] Manual test with real workflow YAML
- [ ] Test math in conditions: `condition: "floor(width) > 5"`

### Documentation
- [ ] Update TASK-059 status to "Superseded by TASK-060"
- [ ] Update TASK-055-FIX-8 with new capabilities
- [ ] Create changelog entry

---

## Acceptance Criteria

### Must Pass
- [ ] All 21 math functions work in UnifiedEvaluator
- [ ] All arithmetic operators work: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- [ ] All comparison operators work: `<`, `<=`, `>`, `>=`, `==`, `!=`
- [ ] All logical operators work: `and`, `or`, `not`
- [ ] Ternary expressions work: `x if condition else y`
- [ ] Chained comparisons work: `0 < x < 10`
- [ ] String comparisons work: `mode == 'EDIT'`
- [ ] `$CALCULATE()` pattern still works
- [ ] `$variable` pattern still works
- [ ] Condition fail-open behavior preserved
- [ ] All existing tests pass unchanged

### New Capabilities
- [ ] Math functions work in conditions: `floor(width) > 5`
- [ ] `evaluate_safe()` method available for error handling

---

## Rollback Plan

If issues arise after deployment:

1. Revert to previous `expression_evaluator.py` and `condition_evaluator.py`
2. Remove `unified_evaluator.py`
3. Revert `__init__.py`

The old code is self-contained, so rollback is straightforward.

---

## Notes

- TASK-059 remains as documentation reference for the logical operators implementation details
- UnifiedEvaluator returns `float` always; wrappers handle type conversion
- `bool` is checked before `int` in `_eval_constant()` (bool is subclass of int)
- Python 3.7 compatibility maintained via `ast.Num`, `ast.Str`, `ast.NameConstant`
- Security maintained via AST node whitelist (no eval, exec, imports)

---

## Related Tasks

- **TASK-059**: Superseded - kept as implementation reference
- **TASK-055-FIX-8**: Documentation to update after completion
- **TASK-056-1**: Extended math functions (already in FUNCTIONS dict)
- **TASK-058**: Loop system (will benefit from ternary support)

---

## Post-Implementation

After TASK-060 is complete:

1. Update TASK-059 header:
   ```markdown
   **Status**: SUPERSEDED by TASK-060
   ```

2. Update TASK-055-FIX-8:
   - Mark comparison operators as ✅
   - Mark logical operators as ✅
   - Mark ternary expressions as ✅
   - Add note about math in conditions

3. Create changelog:
   ```markdown
   # 2025-12-XX: Unified Expression Evaluator (TASK-060)

   - Consolidated ExpressionEvaluator and ConditionEvaluator into unified architecture
   - Added comparison operators to $CALCULATE expressions
   - Added logical operators (and, or, not) to $CALCULATE expressions
   - Added ternary expressions (x if cond else y)
   - NEW: Math functions now work in workflow conditions
   - Full backward compatibility maintained
   ```
