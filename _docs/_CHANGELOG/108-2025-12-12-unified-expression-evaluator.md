# 108 - 2025-12-12: Unified Expression Evaluator

**Status**: ✅ Completed
**Type**: Architecture Refactoring
**Task**: TASK-060
**Complexity**: High (8-10 hours implementation)

---

## Overview

Consolidates two separate evaluators (ExpressionEvaluator and ConditionEvaluator) into a single, well-architected **UnifiedEvaluator**. This prevents technical debt and enables new capabilities like math functions in conditions and ternary expressions in `$CALCULATE()`.

### Key Design Goals Achieved
- Single AST-based evaluation core replacing regex-based ConditionEvaluator
- Domain interface `IExpressionEvaluator` (Clean Architecture compliance)
- Full backward compatibility with existing workflows
- Math functions enabled in conditions (new capability)
- Comparisons and logical operators supported in `$CALCULATE()`

---

## Changes Made

### 1. Domain Interface (NEW)

**File**: `server/router/domain/interfaces/i_expression_evaluator.py`

```python
class IExpressionEvaluator(ABC):
    """Abstract interface for expression evaluation."""

    @abstractmethod
    def set_context(self, context: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_context(self) -> Dict[str, Any]: ...

    @abstractmethod
    def update_context(self, updates: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_variable(self, name: str) -> Optional[Any]: ...

    @abstractmethod
    def evaluate(self, expression: str) -> Any: ...

    @abstractmethod
    def evaluate_safe(self, expression: str, default: Any = 0.0) -> Any: ...
```

### 2. UnifiedEvaluator (NEW)

**File**: `server/router/application/evaluator/unified_evaluator.py` (626 lines)

Core AST-based evaluator supporting:
- **Arithmetic**: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- **Math functions**: 21 functions (abs, min, max, floor, ceil, sqrt, sin, cos, tan, etc.)
- **Comparisons**: `<`, `<=`, `>`, `>=`, `==`, `!=`
- **Chained comparisons**: `0 < x < 10`
- **Logic**: `and`, `or`, `not` (with short-circuit evaluation)
- **Ternary**: `x if condition else y`
- **String comparisons**: `mode == 'EDIT'`

Key methods:
- `evaluate()` - Returns `Any` (float, str)
- `evaluate_as_bool()` - Returns `bool`
- `evaluate_as_float()` - Returns `float`
- `evaluate_safe()` - Returns default on error
- `resolve_computed_parameters()` - Topological sort for dependencies

### 3. ExpressionEvaluator (REFACTORED)

**File**: `server/router/application/evaluator/expression_evaluator.py` (246 lines, was ~466)

Now a thin wrapper that:
- Keeps `$CALCULATE(...)` pattern matching
- Keeps `$variable` direct references
- Keeps context flattening (dimensions → width/height/depth)
- **Delegates evaluation to UnifiedEvaluator**

Removed:
- `_safe_eval()` method
- `_eval_node()` method
- Internal AST parsing code
- `import ast, math, operator`

### 4. ConditionEvaluator (REFACTORED)

**File**: `server/router/application/evaluator/condition_evaluator.py` (196 lines, was ~383)

Now a thin wrapper that:
- Keeps fail-open behavior (returns `True` on error)
- Keeps `simulate_step_effect()` (workflow-specific logic)
- Keeps `set_context_from_scene()` adapter
- **Delegates evaluation to UnifiedEvaluator**

Removed:
- `COMPARISONS` list
- `_parse_or_expression()` method
- `_parse_and_expression()` method
- `_parse_not_expression()` method
- `_parse_primary()` method
- `_split_top_level()` method
- `_resolve_value()` method
- Regex-based parsing code

### 5. Module Exports Updated

**File**: `server/router/application/evaluator/__init__.py`
- Added `UnifiedEvaluator` export

**File**: `server/router/domain/interfaces/__init__.py`
- Added `IExpressionEvaluator` export

---

## New Capabilities

### Math Functions in Conditions
```yaml
# Now possible (was NOT supported before TASK-060)
condition: "floor(table_width / plank_width) > 5"
condition: "sqrt(width * width + depth * depth) < 2.0"
condition: "ceil(count / 2) == 3"
```

### Ternary in $CALCULATE
```yaml
# Now possible (was NOT supported before TASK-060)
computed: "$CALCULATE(0.10 if i <= plank_full_count else plank_remainder_width)"
value: "$CALCULATE(1 if width > 1.0 else 0)"
```

### Comparisons and Logic in $CALCULATE
```yaml
# Now possible
value: "$CALCULATE(10 if a and b else 0)"
value: "$CALCULATE(1 if x > 3 and y < 5 else 2)"
```

---

## Testing

### Backward Compatibility
All 279 existing tests pass without modification:
- `test_expression_evaluator.py` - ✅ Pass
- `test_expression_evaluator_extended.py` - ✅ Pass
- `test_condition_evaluator.py` - ✅ Pass
- `test_condition_evaluator_parentheses.py` - ✅ Pass
- `test_proportion_resolver.py` - ✅ Pass

### New Tests
**File**: `tests/unit/router/application/evaluator/test_unified_evaluator.py`

Test categories:
- Arithmetic operations
- Math functions (all 21)
- Comparison operators
- Chained comparisons
- Logical operators with precedence
- Ternary expressions
- String comparisons
- Boolean literals
- Computed parameters
- Topological sort
- Error handling
- Security (no imports, no eval/exec)

---

## Architecture Decisions

### Why Domain Interface?
1. **Clean Architecture Compliance**: All other router components have interfaces
2. **Dependency Inversion**: High-level modules depend on abstractions
3. **Testability**: Allows mocking evaluator in unit tests

### Why Keep `simulate_step_effect()` in ConditionEvaluator?
1. **Separation of Concerns**: Step simulation is workflow logic, not expression evaluation
2. **Single Responsibility**: UnifiedEvaluator handles math/logic only

### Why `Any` Return Type in UnifiedEvaluator?
1. **String Comparisons**: Need to pass strings for `mode == 'EDIT'`
2. **Type Safety at Wrapper Level**: Wrappers enforce specific types

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `server/router/domain/interfaces/i_expression_evaluator.py` | CREATE | 97 |
| `server/router/domain/interfaces/__init__.py` | MODIFY | +3 |
| `server/router/application/evaluator/unified_evaluator.py` | CREATE | 626 |
| `server/router/application/evaluator/expression_evaluator.py` | REFACTOR | 246 (was ~466) |
| `server/router/application/evaluator/condition_evaluator.py` | REFACTOR | 196 (was ~383) |
| `server/router/application/evaluator/__init__.py` | MODIFY | +1 |
| `tests/unit/router/application/evaluator/test_unified_evaluator.py` | CREATE | ~400 |

**Net result**: ~355 lines removed from wrappers, ~720 lines added (UnifiedEvaluator + interface + tests)

---

## Related Tasks

- **TASK-059**: Superseded by TASK-060 (kept as documentation reference)
- **TASK-055-FIX-8**: Documentation updated
- **TASK-056-1**: Extended math functions (21 functions)
- **TASK-056-5**: Computed parameter dependencies
