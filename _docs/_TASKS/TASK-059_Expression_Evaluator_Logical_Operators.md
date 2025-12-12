# TASK-059: Expression Evaluator - Logical & Comparison Operators

**Status**: TODO
**Priority**: P1 (High - Required for full computed parameter support)
**Estimated Effort**: 3-4 hours
**Dependencies**: TASK-056-1 (Expression Evaluator Extended Functions)
**Related**: TASK-055-FIX-8 (Documentation), TASK-058 (Loop System)
**Created**: 2025-12-12

---

## Problem Statement

Expression evaluator (`expression_evaluator.py`) currently supports **only arithmetic operations**. It lacks:

1. **Comparison operators**: `<`, `<=`, `>`, `>=`, `==`, `!=`
2. **Logical operators**: `and`, `or`, `not`
3. **Ternary expressions**: `x if condition else y`

This prevents workflow authors from using conditional logic in computed parameters.

### Evidence from TASK-055-FIX-8

```yaml
# This DOES NOT WORK:
plank_has_remainder:
  type: int
  computed: "1 if plank_remainder_width > 0.01 else 0"  # ❌ ValueError: Unsupported AST node
  depends_on: ["plank_remainder_width"]
```

**Error**: `ValueError: Unsupported AST node: Compare` or `ValueError: Unsupported AST node: IfExp`

### Root Cause Analysis

**File**: `server/router/application/evaluator/expression_evaluator.py:262-336`

Method `_eval_node()` handles these AST node types:
- ✅ `ast.Constant` - numeric literals
- ✅ `ast.Num` - legacy numeric literals (Python 3.7)
- ✅ `ast.BinOp` - binary operators (`+`, `-`, `*`, `/`, `**`, `%`, `//`)
- ✅ `ast.UnaryOp` - unary operators (`-x`, `+x`)
- ✅ `ast.Call` - function calls (`floor()`, `sin()`, etc.)
- ✅ `ast.Name` - variable references

**Missing handlers**:
- ❌ `ast.Compare` - comparison expressions (`x > y`)
- ❌ `ast.BoolOp` - boolean operators (`x and y`, `x or y`)
- ❌ `ast.UnaryOp(ast.Not)` - logical NOT (`not x`)
- ❌ `ast.IfExp` - ternary expressions (`x if cond else y`)

---

## Requirements

### Must Have (P0)

1. **Comparison operators** in `$CALCULATE`:
   ```yaml
   computed: "$CALCULATE(1 if width > 1.0 else 0)"
   computed: "$CALCULATE(1 if count == 5 else 0)"
   computed: "$CALCULATE(1 if height >= 0.5 else 0)"
   ```

2. **Ternary expressions** in `$CALCULATE`:
   ```yaml
   computed: "$CALCULATE(plank_max_width if i <= plank_full_count else plank_remainder_width)"
   computed: "$CALCULATE(0.1 if is_large else 0.05)"
   ```

3. **Logical operators** in `$CALCULATE`:
   ```yaml
   computed: "$CALCULATE(1 if width > 0.5 and height < 2.0 else 0)"
   computed: "$CALCULATE(1 if is_tall or is_wide else 0)"
   computed: "$CALCULATE(1 if not is_small else 0)"
   ```

4. **Chained comparisons**:
   ```yaml
   computed: "$CALCULATE(1 if 0.5 < width < 2.0 else 0)"  # Python-style chaining
   ```

### Nice to Have (P1)

5. **Nested ternary** (complex branching):
   ```yaml
   computed: "$CALCULATE(0.1 if size == 'small' else (0.2 if size == 'medium' else 0.3))"
   ```

---

## Implementation Plan

### Phase 1: Comparison Operators (ast.Compare)

**File**: `server/router/application/evaluator/expression_evaluator.py`

**Location**: Add after `ast.Name` handler in `_eval_node()` (around line 334)

#### 1.1 Add Comparison Handler

```python
# TASK-059: Comparison expressions
# Handles: ==, !=, <, <=, >, >=
# Also handles chained comparisons: 0 < x < 10
if isinstance(node, ast.Compare):
    left = self._eval_node(node.left)

    # Process all comparisons (handles chained: a < b < c)
    for op, comparator in zip(node.ops, node.comparators):
        right = self._eval_node(comparator)
        if not self._compare_values(left, op, right):
            return 0.0  # False as float
        left = right  # For chained comparisons

    return 1.0  # True as float
```

#### 1.2 Add Comparison Helper Method

```python
def _compare_values(self, left: float, op: ast.cmpop, right: float) -> bool:
    """Compare two values using AST comparison operator.

    TASK-059: Helper for ast.Compare evaluation.

    Args:
        left: Left operand (float).
        op: AST comparison operator node.
        right: Right operand (float).

    Returns:
        Boolean result of comparison.

    Raises:
        ValueError: If comparison operator is not supported.
    """
    compare_ops = {
        ast.Eq: lambda l, r: l == r,
        ast.NotEq: lambda l, r: l != r,
        ast.Lt: lambda l, r: l < r,
        ast.LtE: lambda l, r: l <= r,
        ast.Gt: lambda l, r: l > r,
        ast.GtE: lambda l, r: l >= r,
    }

    op_type = type(op)
    if op_type not in compare_ops:
        raise ValueError(f"Unsupported comparison operator: {op_type.__name__}")

    return compare_ops[op_type](left, right)
```

---

### Phase 2: Logical Operators (ast.BoolOp)

#### 2.1 Add BoolOp Handler

```python
# TASK-059: Boolean operators (and, or)
# Returns 1.0 for True, 0.0 for False
if isinstance(node, ast.BoolOp):
    if isinstance(node.op, ast.And):
        # All values must be truthy (non-zero)
        for value in node.values:
            if not self._eval_node(value):
                return 0.0  # Short-circuit: first False returns False
        return 1.0

    elif isinstance(node.op, ast.Or):
        # At least one value must be truthy
        for value in node.values:
            if self._eval_node(value):
                return 1.0  # Short-circuit: first True returns True
        return 0.0

    raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")
```

---

### Phase 3: Logical NOT (ast.UnaryOp extension)

#### 3.1 Extend UnaryOp Handler

**Current code** (`expression_evaluator.py:305-311`):
```python
# Unary operation
if isinstance(node, ast.UnaryOp):
    operand = self._eval_node(node.operand)
    if isinstance(node.op, ast.USub):
        return -operand
    if isinstance(node.op, ast.UAdd):
        return operand
    raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
```

**Modified code**:
```python
# Unary operation
if isinstance(node, ast.UnaryOp):
    operand = self._eval_node(node.operand)
    if isinstance(node.op, ast.USub):
        return -operand
    if isinstance(node.op, ast.UAdd):
        return operand
    # TASK-059: Logical NOT
    if isinstance(node.op, ast.Not):
        return 0.0 if operand else 1.0  # Invert truthiness
    raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
```

---

### Phase 4: Ternary Expressions (ast.IfExp)

#### 4.1 Add IfExp Handler

```python
# TASK-059: Ternary expressions (x if condition else y)
# Expression: "0.10 if i <= plank_full_count else plank_remainder_width"
if isinstance(node, ast.IfExp):
    # Evaluate condition first
    condition_result = self._eval_node(node.test)

    # Return body if condition is truthy (non-zero), else orelse
    if condition_result:
        return self._eval_node(node.body)
    else:
        return self._eval_node(node.orelse)
```

---

## Complete Implementation

### Updated `_eval_node()` Method

```python
def _eval_node(self, node: ast.AST) -> float:
    """Recursively evaluate AST node.

    TASK-059: Extended with comparison, logical, and ternary operators.

    Args:
        node: AST node to evaluate.

    Returns:
        Evaluated float value.

    Raises:
        ValueError: If node type is not allowed.
    """
    # Constant (Python 3.8+)
    if isinstance(node, ast.Constant):
        # TASK-059: Handle boolean constants BEFORE int/float check
        # (bool is subclass of int, so must check first)
        if isinstance(node.value, bool):
            return 1.0 if node.value else 0.0
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Invalid constant type: {type(node.value)}")

    # Num (Python 3.7 fallback)
    if isinstance(node, ast.Num):
        return float(node.n)

    # NameConstant (Python 3.7 fallback for True/False/None)
    # In Python 3.8+, these are ast.Constant, but 3.7 uses ast.NameConstant
    if isinstance(node, ast.NameConstant):
        if node.value is True:
            return 1.0
        if node.value is False:
            return 0.0
        raise ValueError(f"Invalid NameConstant: {node.value}")

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
        # TASK-059: Logical NOT
        if isinstance(node.op, ast.Not):
            return 0.0 if operand else 1.0
        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

    # Function call
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls allowed")

        func_name = node.func.id
        if func_name not in self.FUNCTIONS:
            raise ValueError(f"Function not allowed: {func_name}")

        args = [self._eval_node(arg) for arg in node.args]
        return float(self.FUNCTIONS[func_name](*args))

    # Name (variable)
    if isinstance(node, ast.Name):
        var_name = node.id
        if var_name in self._context:
            return self._context[var_name]
        # TASK-059: Handle True/False as names (Python compatibility)
        if var_name == "True":
            return 1.0
        if var_name == "False":
            return 0.0
        raise ValueError(f"Unknown variable: {var_name}")

    # TASK-059: Comparison expressions
    if isinstance(node, ast.Compare):
        left = self._eval_node(node.left)

        for op, comparator in zip(node.ops, node.comparators):
            right = self._eval_node(comparator)
            if not self._compare_values(left, op, right):
                return 0.0
            left = right

        return 1.0

    # TASK-059: Boolean operators (and, or)
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            for value in node.values:
                if not self._eval_node(value):
                    return 0.0
            return 1.0

        if isinstance(node.op, ast.Or):
            for value in node.values:
                if self._eval_node(value):
                    return 1.0
            return 0.0

        raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")

    # TASK-059: Ternary expressions (if...else)
    if isinstance(node, ast.IfExp):
        condition_result = self._eval_node(node.test)
        if condition_result:
            return self._eval_node(node.body)
        else:
            return self._eval_node(node.orelse)

    raise ValueError(f"Unsupported AST node: {type(node).__name__}")
```

---

## Test Cases

### File: `tests/unit/router/application/evaluator/test_expression_evaluator_logical.py`

```python
"""
Unit tests for TASK-059: Logical & Comparison Operators.

Tests expression evaluator extensions for:
- Comparison operators (<, <=, >, >=, ==, !=)
- Logical operators (and, or, not)
- Ternary expressions (x if cond else y)
- Chained comparisons (0 < x < 10)
"""

import ast  # Required for TestCompareValuesHelper (ast.Eq, ast.Lt, etc.)
import pytest
from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator


class TestComparisonOperators:
    """Tests for comparison operators in expressions."""

    @pytest.fixture
    def evaluator(self):
        ev = ExpressionEvaluator()
        ev.set_context({"width": 1.5, "height": 0.8, "count": 5})
        return ev

    # Less than
    def test_less_than_true(self, evaluator):
        result = evaluator.evaluate("1 if width < 2.0 else 0")
        assert result == 1.0

    def test_less_than_false(self, evaluator):
        result = evaluator.evaluate("1 if width < 1.0 else 0")
        assert result == 0.0

    # Less than or equal
    def test_less_than_equal_true(self, evaluator):
        result = evaluator.evaluate("1 if width <= 1.5 else 0")
        assert result == 1.0

    def test_less_than_equal_boundary(self, evaluator):
        result = evaluator.evaluate("1 if count <= 5 else 0")
        assert result == 1.0

    # Greater than
    def test_greater_than_true(self, evaluator):
        result = evaluator.evaluate("1 if width > 1.0 else 0")
        assert result == 1.0

    def test_greater_than_false(self, evaluator):
        result = evaluator.evaluate("1 if width > 2.0 else 0")
        assert result == 0.0

    # Greater than or equal
    def test_greater_than_equal_true(self, evaluator):
        result = evaluator.evaluate("1 if height >= 0.8 else 0")
        assert result == 1.0

    # Equal
    def test_equal_true(self, evaluator):
        result = evaluator.evaluate("1 if count == 5 else 0")
        assert result == 1.0

    def test_equal_false(self, evaluator):
        result = evaluator.evaluate("1 if count == 3 else 0")
        assert result == 0.0

    # Not equal
    def test_not_equal_true(self, evaluator):
        result = evaluator.evaluate("1 if count != 3 else 0")
        assert result == 1.0

    def test_not_equal_false(self, evaluator):
        result = evaluator.evaluate("1 if count != 5 else 0")
        assert result == 0.0

    # Chained comparisons
    def test_chained_comparison_true(self, evaluator):
        result = evaluator.evaluate("1 if 1.0 < width < 2.0 else 0")
        assert result == 1.0

    def test_chained_comparison_false(self, evaluator):
        result = evaluator.evaluate("1 if 0.0 < width < 1.0 else 0")
        assert result == 0.0

    def test_chained_triple(self, evaluator):
        result = evaluator.evaluate("1 if 0 < count < 10 else 0")
        assert result == 1.0


class TestLogicalOperators:
    """Tests for logical operators (and, or, not)."""

    @pytest.fixture
    def evaluator(self):
        ev = ExpressionEvaluator()
        ev.set_context({"a": 1.0, "b": 0.0, "c": 1.0, "width": 1.5, "height": 0.8})
        return ev

    # AND operator
    def test_and_both_true(self, evaluator):
        result = evaluator.evaluate("1 if a and c else 0")
        assert result == 1.0

    def test_and_one_false(self, evaluator):
        result = evaluator.evaluate("1 if a and b else 0")
        assert result == 0.0

    def test_and_with_comparisons(self, evaluator):
        result = evaluator.evaluate("1 if width > 1.0 and height < 1.0 else 0")
        assert result == 1.0

    def test_and_multiple(self, evaluator):
        result = evaluator.evaluate("1 if a and c and width > 1.0 else 0")
        assert result == 1.0

    # OR operator
    def test_or_both_true(self, evaluator):
        result = evaluator.evaluate("1 if a or c else 0")
        assert result == 1.0

    def test_or_one_true(self, evaluator):
        result = evaluator.evaluate("1 if a or b else 0")
        assert result == 1.0

    def test_or_both_false(self, evaluator):
        result = evaluator.evaluate("1 if b or 0 else 0")
        assert result == 0.0

    def test_or_with_comparisons(self, evaluator):
        result = evaluator.evaluate("1 if width < 1.0 or height < 1.0 else 0")
        assert result == 1.0

    # NOT operator
    def test_not_true_becomes_false(self, evaluator):
        result = evaluator.evaluate("1 if not a else 0")
        assert result == 0.0

    def test_not_false_becomes_true(self, evaluator):
        result = evaluator.evaluate("1 if not b else 0")
        assert result == 1.0

    def test_not_with_comparison(self, evaluator):
        result = evaluator.evaluate("1 if not width < 1.0 else 0")
        assert result == 1.0

    # Combined operators
    def test_and_or_precedence(self, evaluator):
        # AND has higher precedence than OR
        # a and b or c = (a and b) or c = (True and False) or True = False or True = True
        result = evaluator.evaluate("1 if a and b or c else 0")
        assert result == 1.0

    def test_or_and_precedence(self, evaluator):
        # b or a and c = b or (a and c) = False or (True and True) = False or True = True
        result = evaluator.evaluate("1 if b or a and c else 0")
        assert result == 1.0


class TestTernaryExpressions:
    """Tests for ternary if...else expressions."""

    @pytest.fixture
    def evaluator(self):
        ev = ExpressionEvaluator()
        ev.set_context({
            "width": 1.5,
            "height": 0.8,
            "plank_full_count": 7,
            "plank_max_width": 0.10,
            "plank_remainder_width": 0.03,
            "i": 5
        })
        return ev

    def test_ternary_true_branch(self, evaluator):
        result = evaluator.evaluate("10 if width > 1.0 else 5")
        assert result == 10.0

    def test_ternary_false_branch(self, evaluator):
        result = evaluator.evaluate("10 if width < 1.0 else 5")
        assert result == 5.0

    def test_ternary_with_variables(self, evaluator):
        result = evaluator.evaluate("plank_max_width if i <= plank_full_count else plank_remainder_width")
        assert result == 0.10

    def test_ternary_with_calculation_in_branches(self, evaluator):
        result = evaluator.evaluate("width * 2 if height < 1.0 else width / 2")
        assert result == 3.0  # width * 2 = 1.5 * 2 = 3.0

    def test_ternary_nested(self, evaluator):
        # Small: width < 1.0, Medium: 1.0 <= width < 2.0, Large: width >= 2.0
        result = evaluator.evaluate("0.05 if width < 1.0 else (0.10 if width < 2.0 else 0.15)")
        assert result == 0.10  # width = 1.5, so medium

    def test_ternary_with_logical_condition(self, evaluator):
        result = evaluator.evaluate("1 if width > 1.0 and height < 1.0 else 0")
        assert result == 1.0

    def test_boolean_to_int_pattern(self, evaluator):
        """Test the common pattern: 1 if condition else 0"""
        result = evaluator.evaluate("1 if plank_remainder_width > 0.01 else 0")
        assert result == 1.0  # 0.03 > 0.01


class TestRealWorldScenarios:
    """Tests based on real workflow use cases from TASK-055-FIX-8."""

    @pytest.fixture
    def evaluator(self):
        ev = ExpressionEvaluator()
        ev.set_context({
            "table_width": 0.73,
            "plank_max_width": 0.10,
            "plank_full_count": 7,
            "plank_remainder_width": 0.03,
        })
        return ev

    def test_plank_has_remainder_computed(self, evaluator):
        """Real example from simple_table.yaml"""
        result = evaluator.evaluate("1 if plank_remainder_width > 0.01 else 0")
        assert result == 1.0

    def test_plank_has_no_remainder(self, evaluator):
        evaluator.set_context({
            "table_width": 0.70,
            "plank_max_width": 0.10,
            "plank_full_count": 7,
            "plank_remainder_width": 0.0,
        })
        result = evaluator.evaluate("1 if plank_remainder_width > 0.01 else 0")
        assert result == 0.0

    def test_conditional_plank_width(self, evaluator):
        """Select plank width based on index"""
        evaluator._context["i"] = 5
        result = evaluator.evaluate(
            "plank_max_width if i <= plank_full_count else plank_remainder_width"
        )
        assert result == 0.10

        evaluator._context["i"] = 8
        result = evaluator.evaluate(
            "plank_max_width if i <= plank_full_count else plank_remainder_width"
        )
        assert result == 0.03

    def test_add_stretchers_condition(self, evaluator):
        """Conditional feature based on table size"""
        result = evaluator.evaluate("1 if table_width > 1.0 else 0")
        assert result == 0.0  # 0.73 is not > 1.0

        evaluator._context["table_width"] = 1.5
        result = evaluator.evaluate("1 if table_width > 1.0 else 0")
        assert result == 1.0


class TestEdgeCases:
    """Edge cases and error handling."""

    @pytest.fixture
    def evaluator(self):
        ev = ExpressionEvaluator()
        ev.set_context({"x": 0, "y": 1})
        return ev

    def test_zero_is_falsy(self, evaluator):
        result = evaluator.evaluate("1 if x else 0")
        assert result == 0.0

    def test_non_zero_is_truthy(self, evaluator):
        result = evaluator.evaluate("1 if y else 0")
        assert result == 1.0

    def test_negative_is_truthy(self, evaluator):
        evaluator._context["z"] = -5
        result = evaluator.evaluate("1 if z else 0")
        assert result == 1.0

    def test_comparison_with_zero(self, evaluator):
        result = evaluator.evaluate("1 if x == 0 else 0")
        assert result == 1.0

    def test_boolean_true_false_names(self, evaluator):
        """Test that True/False work as variable names"""
        result = evaluator.evaluate("1 if True else 0")
        assert result == 1.0

        result = evaluator.evaluate("1 if False else 0")
        assert result == 0.0

    def test_boolean_literal_in_expression(self, evaluator):
        """Test boolean literals in arithmetic context"""
        # True should be 1.0, False should be 0.0
        result = evaluator.evaluate("True + 1")
        assert result == 2.0

        result = evaluator.evaluate("False + 1")
        assert result == 1.0

    def test_direct_comparison_result(self, evaluator):
        """Test that comparisons return 1.0/0.0 directly (not just in ternary)"""
        # Direct comparison without ternary wrapper
        result = evaluator.evaluate("(y > x) + 1")  # (1 > 0) = 1.0, + 1 = 2.0
        assert result == 2.0

        result = evaluator.evaluate("(x > y) + 1")  # (0 > 1) = 0.0, + 1 = 1.0
        assert result == 1.0


class TestCompareValuesHelper:
    """Direct tests for _compare_values helper method."""

    @pytest.fixture
    def evaluator(self):
        return ExpressionEvaluator()

    def test_eq(self, evaluator):
        assert evaluator._compare_values(5.0, ast.Eq(), 5.0) is True
        assert evaluator._compare_values(5.0, ast.Eq(), 3.0) is False

    def test_not_eq(self, evaluator):
        assert evaluator._compare_values(5.0, ast.NotEq(), 3.0) is True
        assert evaluator._compare_values(5.0, ast.NotEq(), 5.0) is False

    def test_lt(self, evaluator):
        assert evaluator._compare_values(3.0, ast.Lt(), 5.0) is True
        assert evaluator._compare_values(5.0, ast.Lt(), 3.0) is False

    def test_lte(self, evaluator):
        assert evaluator._compare_values(5.0, ast.LtE(), 5.0) is True
        assert evaluator._compare_values(3.0, ast.LtE(), 5.0) is True

    def test_gt(self, evaluator):
        assert evaluator._compare_values(5.0, ast.Gt(), 3.0) is True
        assert evaluator._compare_values(3.0, ast.Gt(), 5.0) is False

    def test_gte(self, evaluator):
        assert evaluator._compare_values(5.0, ast.GtE(), 5.0) is True
        assert evaluator._compare_values(5.0, ast.GtE(), 3.0) is True


class TestPython37Compatibility:
    """Tests for Python 3.7 compatibility (ast.NameConstant fallback)."""

    @pytest.fixture
    def evaluator(self):
        return ExpressionEvaluator()

    def test_true_literal_works(self, evaluator):
        """True literal should work regardless of Python version"""
        result = evaluator.evaluate("1 + True")
        assert result == 2.0

    def test_false_literal_works(self, evaluator):
        """False literal should work regardless of Python version"""
        result = evaluator.evaluate("1 + False")
        assert result == 1.0

    def test_true_in_condition(self, evaluator):
        """True as condition should return body"""
        result = evaluator.evaluate("5 if True else 10")
        assert result == 5.0

    def test_false_in_condition(self, evaluator):
        """False as condition should return orelse"""
        result = evaluator.evaluate("5 if False else 10")
        assert result == 10.0

    def test_not_true(self, evaluator):
        """not True should be 0.0"""
        result = evaluator.evaluate("1 if not True else 0")
        assert result == 0.0

    def test_not_false(self, evaluator):
        """not False should be 1.0"""
        result = evaluator.evaluate("1 if not False else 0")
        assert result == 1.0
```

---

## Files to Modify

| File | Change | Lines |
|------|--------|-------|
| `server/router/application/evaluator/expression_evaluator.py` | Add `ast.Compare`, `ast.BoolOp`, `ast.IfExp` handlers | 262-336 |
| `server/router/application/evaluator/expression_evaluator.py` | Extend `ast.UnaryOp` for `ast.Not` | 305-311 |
| `server/router/application/evaluator/expression_evaluator.py` | Add `_compare_values()` helper method | NEW |
| `server/router/application/evaluator/expression_evaluator.py` | Handle `True`/`False` in `ast.Name` | 329-334 |
| `server/router/application/evaluator/expression_evaluator.py` | Handle `bool` in `ast.Constant` (check BEFORE int/float!) | 275-278 |
| `server/router/application/evaluator/expression_evaluator.py` | Add `ast.NameConstant` handler (Python 3.7 fallback) | NEW (after ast.Num) |

---

## Documentation Updates

After implementation, update:

1. **`_docs/_TASKS/TASK-055-FIX-8_Computed_Parameters_Expression_Functions.md`**:
   - Change status of comparison/logical operators from ❌ to ✅
   - Update "Available Operators" table
   - Mark examples as working

2. **`_docs/_TASKS/TASK-059_Expression_Evaluator_Logical_Operators.md`**:
   - Mark status as ✅ Done

3. **`_docs/_CHANGELOG/XX-2025-12-XX-expression-logical-operators.md`**:
   - Create changelog entry

---

## Acceptance Criteria

### Phase 1: Comparison Operators
- [ ] `<`, `<=`, `>`, `>=`, `==`, `!=` work in `$CALCULATE`
- [ ] Chained comparisons work (`0 < x < 10`)
- [ ] Unit tests pass for all comparison operators

### Phase 2: Logical Operators
- [ ] `and`, `or` work in `$CALCULATE`
- [ ] `not` works in `$CALCULATE`
- [ ] Short-circuit evaluation implemented
- [ ] Operator precedence correct: `not` > `and` > `or`
- [ ] Unit tests pass for all logical operators

### Phase 3: Ternary Expressions
- [ ] `x if condition else y` works in `$CALCULATE`
- [ ] Nested ternary expressions work
- [ ] Unit tests pass for ternary expressions

### Integration
- [ ] Real workflow example works (`simple_table.yaml` with `plank_has_remainder`)
- [ ] All existing expression evaluator tests still pass
- [ ] Documentation updated (TASK-055-FIX-8)

---

## Estimated Timeline

| Phase | Effort | Description |
|-------|--------|-------------|
| Phase 1: Comparisons | 1 hour | Add `ast.Compare` handler and `_compare_values()` |
| Phase 2: Logical | 1 hour | Add `ast.BoolOp` and extend `ast.UnaryOp` |
| Phase 3: Ternary | 30 min | Add `ast.IfExp` handler |
| Testing | 1 hour | Write and run unit tests |
| Documentation | 30 min | Update TASK-055-FIX-8 and changelog |
| **Total** | **4 hours** | |

---

## Notes

- All new operators return `float` (1.0 for True, 0.0 for False) to maintain type consistency
- Boolean short-circuit evaluation improves performance for complex expressions
- `True`/`False` as variable names supported for Python compatibility
- This task completes the expression evaluator feature set started in TASK-056-1

---

## Important Implementation Notes

### 1. Bool Check Order in `ast.Constant`

**CRITICAL**: In Python, `bool` is a subclass of `int`. Therefore:
```python
isinstance(True, int)  # Returns True!
isinstance(True, bool)  # Returns True
```

The `bool` check **MUST** come **BEFORE** the `int/float` check:
```python
# CORRECT:
if isinstance(node.value, bool):      # Check bool FIRST
    return 1.0 if node.value else 0.0
if isinstance(node.value, (int, float)):
    return float(node.value)

# WRONG (will never reach bool branch):
if isinstance(node.value, (int, float)):  # This catches bool too!
    return float(node.value)
if isinstance(node.value, bool):          # Never reached
    return 1.0 if node.value else 0.0
```

### 2. Python 3.7 Compatibility (ast.NameConstant)

In Python 3.7, `True`/`False`/`None` are represented as `ast.NameConstant`, not `ast.Constant`:
```python
# Python 3.7:
ast.parse("True").body[0].value  # -> ast.NameConstant(value=True)

# Python 3.8+:
ast.parse("True").body[0].value  # -> ast.Constant(value=True)
```

Add handler for both to ensure compatibility.

### 3. Relationship with `ConditionEvaluator`

The codebase has two evaluators:
- **`ExpressionEvaluator`**: AST-based, returns `float`, for `$CALCULATE()` expressions
- **`ConditionEvaluator`**: String/regex-based, returns `bool`, for step conditions

They serve different purposes:
- `ExpressionEvaluator` is used in computed parameters (YAML `computed:` field)
- `ConditionEvaluator` is used in workflow step conditions (YAML `condition:` field)

This task extends `ExpressionEvaluator` only. `ConditionEvaluator` already has full boolean support.

### 4. Test Import Requirements

Tests for `_compare_values()` helper require `import ast` because they instantiate AST operator nodes directly:
```python
import ast  # Required!

def test_eq(self, evaluator):
    assert evaluator._compare_values(5.0, ast.Eq(), 5.0) is True
```

---

## Related Tasks

- **TASK-055-FIX-8**: Documents available functions (needs update after this task)
- **TASK-056-1**: Extended math functions (prerequisite)
- **TASK-058**: Loop system (uses ternary expressions for plank widths)
- **TASK-056-2**: Condition evaluator (separate system, already has boolean support)
