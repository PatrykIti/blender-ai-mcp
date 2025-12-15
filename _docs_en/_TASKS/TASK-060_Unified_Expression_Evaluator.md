# TASK-060: Unified Expression Evaluator

**Status**: ✅ Done (implemented + tested)
**Priority**: P0 (Critical - Pre-launch architecture cleanup)
**Estimated Effort**: 8-10 hours
**Dependencies**: None (replaces TASK-059)
**Related**: TASK-059 (superseded), TASK-055-FIX-8 (documentation), TASK-058 (loop system)
**Created**: 2025-12-12
**Supersedes**: TASK-059 (kept as documentation reference)
**Revised**: 2025-12-12 (Clean Architecture alignment + comprehensive review)
**Revised**: 2025-12-12 (Code review - added critical implementation details)

---

## Executive Summary

Before public launch (Blender forums, Reddit), consolidate two separate evaluators into a single, well-architected **Unified Evaluator**. This prevents technical debt and makes the system easier to extend by future contributors.

**Key Design Goals:**
- Single AST-based evaluation core replacing regex-based ConditionEvaluator
- Domain interface `IExpressionEvaluator` (Clean Architecture compliance)
- Full backward compatibility with existing workflows
- Enable math functions in conditions (new capability)
- Support comparison and logical operators in `$CALCULATE()`

---

## Problem Statement

### Current State: Two Separate Evaluators

```
server/router/application/evaluator/
├── expression_evaluator.py   # AST-based, returns Optional[float]
│   ├── Math: +, -, *, /, floor(), sin(), etc. (22 functions)
│   ├── Comparisons: ❌ NOT SUPPORTED (ValueError: Unsupported AST node)
│   └── Logic: ❌ NOT SUPPORTED
│
└── condition_evaluator.py    # Regex/recursive descent, returns bool
    ├── Math: ❌ NOT SUPPORTED
    ├── Comparisons: ==, !=, <, <=, >, >=
    └── Logic: and, or, not
```

### Current Architecture Issues

| Issue | Impact | Location |
|-------|--------|----------|
| **Two parsers** | Regex parser in ConditionEvaluator has edge cases | `condition_evaluator.py:229-248` |
| **No math in conditions** | `condition: "floor(width) > 5"` fails | `condition_evaluator.py:_parse_primary()` |
| **Duplicated potential** | Adding comparisons to ExpressionEvaluator duplicates logic | TASK-059 approach |
| **Inconsistent behavior** | Risk of `>` working differently in each evaluator | N/A currently |
| **No domain interface** | Unlike other router components, evaluators lack interface | `domain/interfaces/` |
| **Variable substitution** | ExpressionEvaluator uses regex substitution before AST | `expression_evaluator.py:243-251` |

### Evidence from Codebase

**ExpressionEvaluator** (`expression_evaluator.py:262-336`):
- `_eval_node()` handles: `ast.Constant`, `ast.Num`, `ast.BinOp`, `ast.UnaryOp`, `ast.Call`, `ast.Name`
- **Missing**: `ast.Compare`, `ast.BoolOp`, `ast.IfExp`
- Uses regex for variable substitution (lines 243-251) - fragile

**ConditionEvaluator** (`condition_evaluator.py:143-248`):
- Uses recursive descent parser (`_parse_or_expression` → `_parse_and_expression` → etc.)
- String-based comparison (lines 229-235)
- Has critical bug fix for unknown variables (lines 330-339)

### Why Fix Now?

1. **TASK-059** would add comparison/logic to ExpressionEvaluator, creating MORE code in wrong architecture
2. **Public launch imminent** - new contributors need clean codebase
3. **Technical debt cheaper now** than after more workflows depend on current system
4. **Enables future features** - loop system (TASK-058) needs ternary in `$CALCULATE`

---

## Solution Architecture

### Target Structure (Clean Architecture)

```
server/router/
├── domain/
│   └── interfaces/
│       ├── __init__.py                     # Export IExpressionEvaluator
│       └── i_expression_evaluator.py       # NEW: Domain interface
│
└── application/
    └── evaluator/
        ├── __init__.py                     # Export all evaluators
        ├── unified_evaluator.py            # NEW: Core AST-based evaluator
        ├── expression_evaluator.py         # REFACTORED: Wrapper for $CALCULATE
        ├── condition_evaluator.py          # REFACTORED: Wrapper for conditions
        └── proportion_resolver.py          # UNCHANGED
```

### Design Principles

1. **Dependency Inversion (DIP)**: UnifiedEvaluator implements `IExpressionEvaluator` interface
2. **Single Source of Truth**: One AST parser for ALL evaluation (math, comparisons, logic)
3. **Composition over Inheritance**: Wrappers delegate to UnifiedEvaluator
4. **Backward Compatibility**: All existing tests pass without modification
5. **Type Safety**: Core returns `Any`, wrappers enforce type contracts (`float` / `bool`)
6. **Separation of Concerns**: `simulate_step_effect()` stays in ConditionEvaluator (workflow logic)

### Component Responsibilities

| Component | Input | Output | Responsibility |
|-----------|-------|--------|----------------|
| **UnifiedEvaluator** | Expression string | `Any` (float/str) | AST-based evaluation core |
| **ExpressionEvaluator** | `$CALCULATE(...)` | `Optional[float]` | Pattern matching, context flattening |
| **ConditionEvaluator** | Condition string | `bool` | Fail-open, step simulation |
| **ProportionResolver** | `$AUTO_*` | `float`/`list` | Dimension-relative calculations |

---

## Requirements

### Must Have (P0)

1. **Domain Interface** `IExpressionEvaluator`:
   - Abstract contract for expression evaluation
   - Methods: `set_context()`, `get_context()`, `update_context()`, `get_variable()`, `evaluate()`, `evaluate_safe()`
   - Enables dependency injection in tests and future implementations

2. **UnifiedEvaluator** with full feature set:
   - **Arithmetic**: `+`, `-`, `*`, `/`, `//`, `%`, `**`
   - **Math functions**: All 22 from TASK-056-1 (abs, min, max, floor, ceil, sqrt, sin, cos, tan, etc.)
   - **Comparisons**: `<`, `<=`, `>`, `>=`, `==`, `!=`
   - **Logic**: `and`, `or`, `not`
   - **Ternary**: `x if condition else y`
   - **Chained comparisons**: `0 < x < 10`
   - **String comparisons**: `mode == 'EDIT'`
   - **Computed parameters**: `resolve_computed_parameters()` with topological sort
   - **Helper methods**: `evaluate_as_bool()`, `evaluate_as_float()`

3. **ExpressionEvaluator** wrapper (backward compatible):
   - `$CALCULATE(...)` pattern matching (unchanged)
   - `$variable` references (unchanged)
   - Context flattening: `dimensions` → `width/height/depth`, `proportions` → `proportions_*`
   - Returns `Optional[float]` (unchanged)
   - **Delegates to UnifiedEvaluator** internally

4. **ConditionEvaluator** wrapper (backward compatible):
   - Returns `bool` (unchanged)
   - Fail-open behavior: returns `True` on error (unchanged)
   - **Preserves `simulate_step_effect()`** - workflow-specific logic stays here
   - `set_context_from_scene()` method (unchanged)
   - **Delegates to UnifiedEvaluator** for evaluation

5. **All existing tests pass** without ANY modification:
   - `test_expression_evaluator.py` (344 lines)
   - `test_expression_evaluator_extended.py` (TASK-056-1)
   - `test_condition_evaluator.py` (383 lines)
   - `test_condition_evaluator_parentheses.py` (TASK-056-2)

### Nice to Have (P1) - Enabled by This Refactor

6. **Math functions in conditions**:
   ```yaml
   condition: "floor(table_width / plank_width) > 5"
   condition: "sqrt(width * width + depth * depth) < 2.0"
   ```

7. **Ternary in expressions**:
   ```yaml
   # In computed parameters:
   computed: "0.10 if i <= plank_full_count else plank_remainder_width"

   # In step parameters:
   some_value: "$CALCULATE(0.10 if i <= plank_full_count else plank_remainder_width)"
   ```

8. **Consistent error messages** across both wrappers

---

## Implementation Plan

### Phase 1: Create Domain Interface

**File**: `server/router/domain/interfaces/i_expression_evaluator.py`

```python
"""
Expression Evaluator Interface.

TASK-060: Domain interface for expression evaluation.
Defines contract for safe expression evaluation used by workflow system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IExpressionEvaluator(ABC):
    """Abstract interface for expression evaluation.

    Supports mathematical expressions, comparisons, and logical operations.
    All implementations must provide safe evaluation without arbitrary code execution.

    Implementations:
        - UnifiedEvaluator: Full AST-based implementation

    Example:
        evaluator: IExpressionEvaluator = UnifiedEvaluator()
        evaluator.set_context({"width": 2.0, "mode": "EDIT"})
        result = evaluator.evaluate("width > 1.0")  # -> 1.0
    """

    @abstractmethod
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dictionary with variable values.
                     Supports: int, float, bool, str values.
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
        """Update context with new values (merge).

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
            Evaluated value:
            - float for arithmetic expressions
            - float (1.0/0.0) for comparisons/logic (represents True/False)
            - str only in string literal contexts

        Raises:
            ValueError: If expression is invalid or uses disallowed constructs.
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

Add to existing exports:
```python
from server.router.domain.interfaces.i_expression_evaluator import (
    IExpressionEvaluator,
)

__all__ = [
    # ... existing exports ...
    # Expression Evaluator (TASK-060)
    "IExpressionEvaluator",
]
```

---

### Phase 2: Create UnifiedEvaluator (Core Implementation)

**File**: `server/router/application/evaluator/unified_evaluator.py`

Key implementation details:

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

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dictionary with variable values.
                     Supports: int, float, bool, str values.
        """
        self._context = {}
        for key, value in context.items():
            if isinstance(value, bool):
                # CRITICAL: Check bool BEFORE int (bool is subclass of int)
                self._context[key] = 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                self._context[key] = float(value)
            elif isinstance(value, str):
                # Store strings for comparison (e.g., mode == 'EDIT')
                self._context[key] = value
            # Ignore other types (lists, dicts, etc.)

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
```

---

### Phase 3: Refactor ExpressionEvaluator (Wrapper)

**File**: `server/router/application/evaluator/expression_evaluator.py`

Key changes:
- Remove internal `_safe_eval()`, `_eval_node()` methods
- Add `self._unified = UnifiedEvaluator()`
- Delegate `evaluate()` to `self._unified.evaluate_as_float()`
- Keep ALL context flattening logic (dimensions, proportions)
- Keep ALL pattern matching (`$CALCULATE`, `$variable`)
- Keep `FUNCTIONS` as class attribute (backward compatibility)

```python
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
    - Context flattening (dimensions → width/height/depth)
    - Backward-compatible API

    TASK-060: Now delegates evaluation to UnifiedEvaluator.
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
```

---

### Phase 4: Refactor ConditionEvaluator (Wrapper)

**File**: `server/router/application/evaluator/condition_evaluator.py`

Key changes:
- Remove internal parser methods (`_parse_or_expression`, etc.)
- Remove `COMPARISONS` list
- Add `self._unified = UnifiedEvaluator()`
- Delegate `evaluate()` to `self._unified.evaluate_as_bool()`
- **KEEP** `simulate_step_effect()` - this is workflow logic, not evaluation
- **KEEP** `set_context_from_scene()` - this is adapter logic

```python
"""
Condition Evaluator.

Evaluates boolean conditions for workflow step execution.
Supports comparisons, boolean variables, and logical operators.

TASK-041-10: Original implementation
TASK-060: Refactored to delegate to UnifiedEvaluator.
"""

import logging
from typing import Dict, Any

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates boolean conditions for workflow step execution.

    This is a wrapper around UnifiedEvaluator that provides:
    - Boolean return type (converts result to bool)
    - Fail-open behavior (returns True on error)
    - Step effect simulation (simulate_step_effect)
    - SceneContext adapter (set_context_from_scene)

    TASK-060: Now delegates evaluation to UnifiedEvaluator.
    NEW capabilities:
    - Math functions in conditions: "floor(width) > 5"
    - Ternary expressions: "1 if has_selection else 0"

    Supported conditions:
    - "current_mode != 'EDIT'"
    - "has_selection"
    - "not has_selection"
    - "object_count > 0"
    - "width > 1.0 and height < 2.0"
    - "floor(table_width / plank_width) > 5"  # NEW in TASK-060
    """

    def __init__(self):
        """Initialize condition evaluator."""
        self._unified = UnifiedEvaluator()

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set evaluation context.

        Args:
            context: Dictionary with variable values.

        Expected keys:
        - current_mode: str (e.g., "OBJECT", "EDIT", "SCULPT")
        - has_selection: bool
        - object_count: int
        - active_object: str (object name)
        - selected_verts, selected_edges, selected_faces: int
        """
        self._unified.set_context(context)

    def set_context_from_scene(self, scene_context: Any) -> None:
        """Set context from SceneContext object.

        Args:
            scene_context: SceneContext instance.
        """
        context: Dict[str, Any] = {
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
            return True  # Fail-open: execute step if condition can't be evaluated

    def simulate_step_effect(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Simulate the effect of a workflow step on context.

        Updates the context to reflect what would happen after
        executing a tool. Used for conditional step evaluation
        within a workflow.

        NOTE: This method is NOT delegated to UnifiedEvaluator because
        it's workflow-specific logic, not expression evaluation logic.

        Args:
            tool_name: Name of the tool being executed.
            params: Tool parameters.
        """
        updates: Dict[str, Any] = {}

        if tool_name == "system_set_mode":
            mode = params.get("mode")
            if mode:
                updates["current_mode"] = mode

        elif tool_name == "scene_set_mode":
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
            # Targeted selection typically results in some selection
            updates["has_selection"] = True

        elif tool_name == "modeling_create_primitive":
            # Creating an object increases object count
            current_count = self._unified.get_context().get("object_count", 0)
            updates["object_count"] = current_count + 1

        elif tool_name == "scene_delete_object":
            # Deleting an object decreases object count
            current_count = self._unified.get_context().get("object_count", 0)
            if current_count > 0:
                updates["object_count"] = current_count - 1

        if updates:
            self._unified.update_context(updates)
```

---

### Phase 5: Update Module Exports

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

Test categories based on TASK-059 specification:

1. **Arithmetic Operations** - From existing `test_expression_evaluator.py`
2. **Math Functions** - All 22 functions
3. **Comparison Operators** - `<`, `<=`, `>`, `>=`, `==`, `!=`
4. **Chained Comparisons** - `0 < x < 10`
5. **Logical Operators** - `and`, `or`, `not` with precedence
6. **Ternary Expressions** - `x if condition else y`
7. **String Comparisons** - `mode == 'EDIT'`
8. **Boolean Literals** - `True`, `False`
9. **Context Management** - `set_context`, `update_context`, `get_variable`
10. **Computed Parameters** - topological sort, circular dependency
11. **Error Handling** - empty, syntax, unknown vars, type errors
12. **Security** - no imports, no eval/exec, no attribute access

### Phase 7: Backward Compatibility (CRITICAL)

**All existing tests MUST pass without modification:**

```bash
# Run before AND after implementation
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/ -v
```

Files that must pass unchanged:
- `test_expression_evaluator.py`
- `test_expression_evaluator_extended.py`
- `test_condition_evaluator.py`
- `test_condition_evaluator_parentheses.py`
- `test_proportion_resolver.py` (should be unaffected)

### Phase 8: Integration Tests

**File**: `tests/unit/router/application/evaluator/test_unified_integration.py`

Test integration with WorkflowRegistry:
- `expand_workflow()` with conditions
- `resolve_computed_parameters_for_workflow()`
- Math functions in workflow conditions

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `server/router/domain/interfaces/i_expression_evaluator.py` | **CREATE** | Domain interface |
| `server/router/domain/interfaces/__init__.py` | **MODIFY** | Export IExpressionEvaluator |
| `server/router/application/evaluator/unified_evaluator.py` | **CREATE** | Core AST-based evaluator |
| `server/router/application/evaluator/expression_evaluator.py` | **MODIFY** | Delegate to UnifiedEvaluator |
| `server/router/application/evaluator/condition_evaluator.py` | **MODIFY** | Delegate to UnifiedEvaluator |
| `server/router/application/evaluator/__init__.py` | **MODIFY** | Export UnifiedEvaluator |
| `tests/unit/router/application/evaluator/test_unified_evaluator.py` | **CREATE** | Core unit tests |
| `tests/unit/router/application/evaluator/test_unified_integration.py` | **CREATE** | Integration tests |

---

## Migration Checklist

### Before Implementation
- [x] Run all existing evaluator tests, capture output
- [x] Read `expression_evaluator.py` thoroughly (466 lines)
- [x] Read `condition_evaluator.py` thoroughly (383 lines)
- [x] Understand `WorkflowRegistry` integration points

### Implementation
- [x] Phase 1: Create `i_expression_evaluator.py`
- [x] Phase 2: Create `unified_evaluator.py`
- [x] Phase 3: Refactor `expression_evaluator.py`
- [x] Phase 4: Refactor `condition_evaluator.py`
- [x] Phase 5: Update `__init__.py` and domain interfaces
- [x] Phase 6: Write `test_unified_evaluator.py`
- [x] Phase 7: Verify all existing tests pass
- [x] Phase 8: Write integration tests

### Verification
- [x] All existing tests pass (backward compatibility)
- [x] All new tests pass
- [x] Manual test: `condition: "floor(width) > 5"` works
- [x] Manual test: `mode == 'EDIT'` works in conditions
- [x] Manual test: `$CALCULATE(x if y > 0 else z)` works
- [x] Manual test: simple_table workflow with computed params works

### Documentation
- [x] Update TASK-059 header: "⚠️ SUPERSEDED by TASK-060"
- [x] Update TASK-055-FIX-8 with new operators
- [x] Create changelog entry
- [x] Create `_docs/_ROUTER/IMPLEMENTATION/36-unified-evaluator.md`

---

## Acceptance Criteria

### Must Pass (P0)

- [x] `IExpressionEvaluator` interface exists in domain layer
- [x] `UnifiedEvaluator` implements `IExpressionEvaluator`
- [x] All 22 math functions work in UnifiedEvaluator
- [x] All arithmetic operators work: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- [x] All comparison operators work: `<`, `<=`, `>`, `>=`, `==`, `!=`
- [x] All logical operators work: `and`, `or`, `not`
- [x] Ternary expressions work: `x if condition else y`
- [x] Chained comparisons work: `0 < x < 10`
- [x] String comparisons work: `mode == 'EDIT'`
- [x] `$CALCULATE()` pattern still works (backward compatible)
- [x] `$variable` pattern still works (backward compatible)
- [x] Condition fail-open behavior preserved (returns True on error)
- [x] `simulate_step_effect()` preserved in ConditionEvaluator
- [x] `resolve_computed_parameters()` works with dependencies
- [x] **All 5 existing test files pass unchanged**

### New Capabilities (P1)

- [x] Math functions work in conditions: `floor(width) > 5`
- [x] `evaluate_as_bool()` method available
- [x] `evaluate_as_float()` method available
- [x] `evaluate_safe()` method available

---

## Architectural Decisions

### Why Domain Interface?

1. **Clean Architecture Compliance**: All other router components have interfaces (`IInterceptor`, `ISceneAnalyzer`, `IMatcher`, etc.)
2. **Dependency Inversion**: High-level modules depend on abstractions
3. **Testability**: Allows mocking evaluator in unit tests
4. **Extensibility**: Could have cached evaluator, remote evaluator, etc.

### Why `Any` Return Type in UnifiedEvaluator?

1. **String Comparisons**: Need to pass strings for `mode == 'EDIT'`
2. **Type Safety at Wrapper Level**: ExpressionEvaluator enforces `float`, ConditionEvaluator enforces `bool`
3. **Ternary Flexibility**: Different branches can return different types

### Why Keep `simulate_step_effect()` in ConditionEvaluator?

1. **Separation of Concerns**: Step simulation is workflow logic, not expression evaluation
2. **Single Responsibility**: UnifiedEvaluator handles math/logic only
3. **Backward Compatibility**: WorkflowRegistry calls it on ConditionEvaluator

### Why No Regex Variable Substitution?

Current ExpressionEvaluator uses regex to replace variables before AST parsing (lines 243-251).
UnifiedEvaluator handles variables directly in `_eval_name()`:
- More robust (no edge cases with variable names containing others)
- Cleaner code
- Direct context lookup

---

## Critical Implementation Details (Code Review 2025-12-12)

### 1. Context Type Consistency

**Problem**: Current `ExpressionEvaluator._context` is typed as `Dict[str, float]`, but `UnifiedEvaluator._context` needs `Dict[str, Any]` (to support strings).

**Solution**:
- `UnifiedEvaluator._context: Dict[str, Any]` - stores floats AND strings
- `ExpressionEvaluator.get_context() -> Dict[str, float]` - filters out strings for backward compatibility
- `ConditionEvaluator.get_context() -> Dict[str, Any]` - returns full context

```python
# ExpressionEvaluator wrapper
def get_context(self) -> Dict[str, float]:
    """Get current evaluation context (numeric values only)."""
    ctx = self._unified.get_context()
    return {k: v for k, v in ctx.items() if isinstance(v, (int, float))}
```

### 2. Missing `update_context()` in ExpressionEvaluator

**Problem**: TASK-060 spec doesn't show `update_context()` in ExpressionEvaluator, but this method may be needed for consistency.

**Solution**: Add to ExpressionEvaluator wrapper:
```python
def update_context(self, updates: Dict[str, Any]) -> None:
    """Update context with new values (merge)."""
    self._unified.update_context(updates)
```

### 3. `depends_on` None Check

**Problem**: Current code doesn't handle `schema.depends_on = None` properly.

**Current** (`expression_evaluator.py:387`):
```python
graph = {
    name: (schema.depends_on if hasattr(schema, "depends_on") else [])
    ...
}
```

**Fixed** (in UnifiedEvaluator):
```python
graph = {
    name: (schema.depends_on if hasattr(schema, "depends_on") and schema.depends_on else [])
    ...
}
```

### 4. WorkflowRegistry Integration Points

**File**: `server/router/application/workflows/registry.py`

The following methods interact with evaluators:

| Method | Evaluator Used | Must Preserve |
|--------|---------------|---------------|
| `expand_workflow()` | All three | Context setup order |
| `_build_condition_context()` | ConditionEvaluator | Context normalization |
| `_resolve_single_value()` | ExpressionEvaluator | `$CALCULATE()` pattern |
| `_steps_to_calls()` | ConditionEvaluator | `simulate_step_effect()` |

**Critical**: `simulate_step_effect()` must modify the same context that `evaluate()` reads:
```python
# In ConditionEvaluator
def simulate_step_effect(self, tool_name: str, params: Dict[str, Any]) -> None:
    updates = {}
    # ... build updates ...
    if updates:
        self._unified.update_context(updates)  # ← Must use unified's context
```

### 5. String Handling in Conditions

**Current ConditionEvaluator** handles strings via `_resolve_value()` (lines 304-306):
```python
if (value_str.startswith("'") and value_str.endswith("'")) or \
   (value_str.startswith('"') and value_str.endswith('"')):
    return value_str[1:-1]
```

**UnifiedEvaluator** handles strings in `_eval_constant()`:
```python
if isinstance(value, str):
    return value  # Return string for comparisons
```

**Key difference**: UnifiedEvaluator gets strings from AST (`ast.Constant` with `str` value), while ConditionEvaluator strips quotes manually.

### 6. Unknown Variable Handling (Critical Bug Fix)

**Current ConditionEvaluator** (`condition_evaluator.py:330-339`):
```python
# Return 0 for numeric comparisons (fail-safe: condition will be False)
return 0
```

**UnifiedEvaluator** must maintain this behavior:
```python
def _eval_name(self, node: ast.Name) -> Any:
    var_name = node.id
    if var_name in self._context:
        return self._context[var_name]
    if var_name in ("True", "False"):
        return 1.0 if var_name == "True" else 0.0
    # CRITICAL: Raise for ExpressionEvaluator, but ConditionEvaluator catches and returns True
    raise ValueError(f"Unknown variable: {var_name}")
```

**ConditionEvaluator wrapper** catches this:
```python
def evaluate(self, condition: str) -> bool:
    try:
        result = self._unified.evaluate_as_bool(condition)
        return result
    except Exception as e:
        logger.warning(f"Condition evaluation failed: '{condition}' - {e}")
        return True  # Fail-open
```

### 7. Test File Compatibility Matrix

| Test File | Tests | Must Pass Unchanged |
|-----------|-------|---------------------|
| `test_expression_evaluator.py` | ~50 tests | ✅ Yes |
| `test_expression_evaluator_extended.py` | ~40 tests | ✅ Yes |
| `test_condition_evaluator.py` | ~60 tests | ✅ Yes |
| `test_condition_evaluator_parentheses.py` | ~30 tests | ✅ Yes |
| `test_proportion_resolver.py` | ~25 tests | ✅ Yes (unaffected) |

**Run before AND after implementation**:
```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/ -v --tb=short
```

### 8. Interface Pattern (follow IMatcher)

Follow the pattern from `server/router/domain/interfaces/matcher.py`:

```python
# i_expression_evaluator.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IExpressionEvaluator(ABC):
    """Abstract interface for expression evaluation.

    Implementations:
        - UnifiedEvaluator: Full AST-based implementation

    Example:
        evaluator: IExpressionEvaluator = UnifiedEvaluator()
        evaluator.set_context({"width": 2.0, "mode": "EDIT"})
        result = evaluator.evaluate("width > 1.0")  # -> 1.0
    """

    @abstractmethod
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation."""
        pass

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context."""
        pass

    @abstractmethod
    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values (merge)."""
        pass

    @abstractmethod
    def get_variable(self, name: str) -> Optional[Any]:
        """Get variable value from context."""
        pass

    @abstractmethod
    def evaluate(self, expression: str) -> Any:
        """Evaluate expression and return result."""
        pass

    @abstractmethod
    def evaluate_safe(self, expression: str, default: Any = 0.0) -> Any:
        """Evaluate expression with fallback on error."""
        pass
```

### 9. Comparison with Floats (Edge Case)

**Problem**: Float comparisons like `0.1 + 0.2 == 0.3` fail due to floating point precision.

**Current behavior**: Both evaluators use exact comparison.

**Decision**: Keep exact comparison (matches Python semantics). Document in workflow guidelines that floating point comparisons should use range checks:
```yaml
# Bad: 0.1 + 0.2 == 0.3  (may fail due to float precision)
# Good: abs(result - 0.3) < 0.001
```

### 10. Boolean Short-Circuit Evaluation

**UnifiedEvaluator** must implement proper short-circuit:

```python
def _eval_boolop(self, node: ast.BoolOp) -> float:
    if isinstance(node.op, ast.And):
        for value in node.values:
            result = self._eval_node(value)
            if not result:
                return 0.0  # Short-circuit: first False
        return 1.0

    if isinstance(node.op, ast.Or):
        for value in node.values:
            result = self._eval_node(value)
            if result:
                return 1.0  # Short-circuit: first True
        return 0.0
```

**Why it matters**: Expressions like `has_obj and obj.selected` should NOT evaluate `obj.selected` if `has_obj` is False.

---

## Rollback Plan

If issues arise after deployment:

1. `git revert` the TASK-060 commit
2. Old code is self-contained, rollback is straightforward
3. Domain interface can be left (no harm)

---

## Related Tasks

- **TASK-059**: Superseded - kept as implementation reference for test cases
- **TASK-055-FIX-8**: Documentation to update after completion
- **TASK-056-1**: Extended math functions (22 functions in FUNCTIONS dict)
- **TASK-056-5**: Computed parameter dependencies (topological sort)
- **TASK-058**: Loop system (will benefit from ternary in $CALCULATE)

---

## Post-Implementation Checklist

1. Update `_docs/_TASKS/TASK-059_Expression_Evaluator_Logical_Operators.md`:
   ```markdown
   **Status**: ⚠️ SUPERSEDED by TASK-060
   ```

2. Create `_docs/_CHANGELOG/XX-2025-12-XX-unified-evaluator.md`

3. Update `_docs/_TASKS/README.md`:
   - Move TASK-060 to Done section
   - Add note about TASK-059 being superseded

4. Create `_docs/_ROUTER/IMPLEMENTATION/XX-unified-evaluator.md`

---

## Implementation Order (Step-by-Step)

**IMPORTANT**: Follow this exact order to maintain backward compatibility at each step.

### Step 1: Run Baseline Tests
```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/ -v --tb=short > baseline_tests.txt
```
Save output to compare later.

### Step 2: Create Domain Interface
1. Create `server/router/domain/interfaces/i_expression_evaluator.py`
2. Update `server/router/domain/interfaces/__init__.py` (add export)
3. Run tests → should pass (no functional change)

### Step 3: Create UnifiedEvaluator
1. Create `server/router/application/evaluator/unified_evaluator.py`
2. Update `server/router/application/evaluator/__init__.py` (add export)
3. Create `tests/unit/router/application/evaluator/test_unified_evaluator.py`
4. Run tests → should pass (new tests only)

### Step 4: Refactor ExpressionEvaluator
1. Backup current implementation: `cp expression_evaluator.py expression_evaluator.py.bak`
2. Refactor to wrapper
3. Run tests → **ALL existing tests MUST pass**
```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/test_expression_evaluator*.py -v
```

### Step 5: Refactor ConditionEvaluator
1. Backup current implementation: `cp condition_evaluator.py condition_evaluator.py.bak`
2. Refactor to wrapper
3. Run tests → **ALL existing tests MUST pass**
```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/test_condition_evaluator*.py -v
```

### Step 6: Integration Test
```bash
# Run ALL evaluator tests
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/ -v

# Run workflow tests (uses evaluators)
PYTHONPATH=. poetry run pytest tests/unit/router/application/workflows/ -v

# Run full router tests
PYTHONPATH=. poetry run pytest tests/unit/router/ -v
```

### Step 7: Manual E2E Test
Test with actual workflow that uses conditions:
```bash
ROUTER_ENABLED=true poetry run python -c "
from server.router.application.workflows.registry import WorkflowRegistry
registry = WorkflowRegistry()
registry.load_custom_workflows()

# Test condition with math function (NEW capability)
from server.router.application.evaluator import ConditionEvaluator
ce = ConditionEvaluator()
ce.set_context({'width': 2.5, 'mode': 'EDIT'})
print('floor(width) > 2:', ce.evaluate('floor(width) > 2'))  # Should be True

# Test ternary in $CALCULATE (NEW capability)
from server.router.application.evaluator import ExpressionEvaluator
ee = ExpressionEvaluator()
ee.set_context({'count': 5, 'max_count': 7})
print('ternary:', ee.evaluate('0.1 if count <= max_count else 0.05'))  # Should be 0.1
"
```

### Step 8: Cleanup
1. Remove backup files (`.bak`)
2. Verify no dead code remains
3. Update documentation

---

## Code to Remove (After Refactoring)

### ExpressionEvaluator - REMOVE these methods/imports:

```python
# REMOVE from imports:
import ast
import math
import operator

# REMOVE these methods entirely (moved to UnifiedEvaluator):
def _safe_eval(self, expression: str) -> float:
    """..."""  # ~35 lines - DELETE

def _eval_node(self, node: ast.AST) -> float:
    """..."""  # ~75 lines - DELETE

def _topological_sort(self, graph: Dict[str, list]) -> list:
    """..."""  # ~30 lines - DELETE

# REMOVE class attribute (will reference UnifiedEvaluator.FUNCTIONS instead):
FUNCTIONS = {
    "abs": abs,
    "min": min,
    # ... all 22 functions
}  # ~30 lines - DELETE (but keep as `FUNCTIONS = UnifiedEvaluator.FUNCTIONS`)
```

**Lines to remove from `expression_evaluator.py`**: ~170 lines (out of 466)

### ConditionEvaluator - REMOVE these methods/imports:

```python
# REMOVE from imports:
import re  # (if no longer needed after removing regex parsing)

# REMOVE class attribute:
COMPARISONS = [
    (">=", lambda a, b: a >= b),
    # ...
]  # ~8 lines - DELETE

# REMOVE these methods entirely (moved to UnifiedEvaluator):
def _evaluate_expression(self, condition: str) -> bool:
    """..."""  # ~15 lines - DELETE

def _parse_or_expression(self, condition: str) -> bool:
    """..."""  # ~15 lines - DELETE

def _parse_and_expression(self, condition: str) -> bool:
    """..."""  # ~15 lines - DELETE

def _parse_not_expression(self, condition: str) -> bool:
    """..."""  # ~10 lines - DELETE

def _parse_primary(self, condition: str) -> bool:
    """..."""  # ~40 lines - DELETE

def _split_top_level(self, condition: str, delimiter: str) -> list:
    """..."""  # ~30 lines - DELETE

def _resolve_value(self, value_str: str) -> Any:
    """..."""  # ~50 lines - DELETE
```

**Lines to remove from `condition_evaluator.py`**: ~185 lines (out of 383)

### Summary of Removals

| File | Current Lines | Remove | Final Lines |
|------|---------------|--------|-------------|
| `expression_evaluator.py` | 466 | ~170 | ~150 |
| `condition_evaluator.py` | 383 | ~185 | ~100 |
| **Total removed** | | **~355** | |
| `unified_evaluator.py` | N/A | N/A | ~450 (NEW) |

**Net change**: +~100 lines, but with:
- Single source of truth for AST evaluation
- Full feature set (comparisons + logic in both evaluators)
- Domain interface for testability
- No code duplication

### Final File Structure After Refactoring

```
server/router/
├── domain/
│   └── interfaces/
│       ├── __init__.py                     # +1 export: IExpressionEvaluator
│       └── i_expression_evaluator.py       # NEW: ~80 lines
│
└── application/
    └── evaluator/
        ├── __init__.py                     # +1 export: UnifiedEvaluator
        ├── unified_evaluator.py            # NEW: ~450 lines (core AST engine)
        ├── expression_evaluator.py         # REFACTORED: ~150 lines (was 466)
        ├── condition_evaluator.py          # REFACTORED: ~100 lines (was 383)
        └── proportion_resolver.py          # UNCHANGED: 309 lines
```

### Final ExpressionEvaluator Structure (~150 lines)

```python
"""Expression Evaluator - Wrapper for $CALCULATE() expressions."""

import re
import logging
from typing import Dict, Any, Optional

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator

class ExpressionEvaluator:
    CALCULATE_PATTERN = re.compile(...)
    VARIABLE_PATTERN = re.compile(...)
    FUNCTIONS = UnifiedEvaluator.FUNCTIONS  # Reference, not copy

    def __init__(self): ...
    def set_context(self, context): ...      # Context flattening logic KEPT
    def get_context(self): ...
    def update_context(self, updates): ...
    def evaluate(self, expression): ...      # Delegates to _unified
    def resolve_param_value(self, value): ...
    def resolve_params(self, params): ...
    def resolve_computed_parameters(...): ...  # Delegates to _unified
```

### Final ConditionEvaluator Structure (~100 lines)

```python
"""Condition Evaluator - Wrapper for boolean conditions."""

import logging
from typing import Dict, Any

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator

class ConditionEvaluator:
    def __init__(self): ...
    def set_context(self, context): ...
    def set_context_from_scene(self, scene_context): ...  # KEPT (adapter logic)
    def get_context(self): ...
    def update_context(self, updates): ...
    def evaluate(self, condition): ...           # Delegates to _unified + fail-open
    def simulate_step_effect(self, tool, params): ...  # KEPT (workflow logic)
```

---

## Quick Reference: What Changes vs What Stays

### STAYS THE SAME (Backward Compatibility)
- `ExpressionEvaluator` class name and location
- `ConditionEvaluator` class name and location
- All public method signatures
- `$CALCULATE()` pattern matching
- `$variable` pattern matching
- Context flattening (dimensions → width/height/depth)
- Fail-open behavior in ConditionEvaluator
- `simulate_step_effect()` method

### CHANGES (Internal)
- Evaluation delegated to `UnifiedEvaluator`
- Regex-based parsing → AST-based parsing (in UnifiedEvaluator)
- Internal `_safe_eval()`, `_eval_node()` methods removed from ExpressionEvaluator
- Internal `_parse_*()` methods removed from ConditionEvaluator

### NEW CAPABILITIES
- Math functions in conditions: `floor(width) > 5`
- Ternary in `$CALCULATE`: `0.1 if x > 0 else 0.05`
- Comparisons in `$CALCULATE`: `1 if width > 1.0 else 0`
- Logical operators in `$CALCULATE`: `1 if a and b else 0`
- `IExpressionEvaluator` interface in domain layer
