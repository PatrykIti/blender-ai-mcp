# 36 - Unified Expression Evaluator

**TASK-060** | Status: ✅ Implemented | Complexity: High

---

## Overview

The **UnifiedEvaluator** consolidates two separate evaluation systems into a single AST-based core. This eliminates code duplication, enables new capabilities, and follows Clean Architecture principles.

### Before TASK-060
```
ExpressionEvaluator (466 lines)    ConditionEvaluator (383 lines)
├── _safe_eval() with ast.parse     ├── COMPARISONS list
├── _eval_node() recursive          ├── _parse_or_expression()
├── Math functions (22)             ├── _parse_and_expression()
└── $CALCULATE pattern              ├── _parse_not_expression()
                                    ├── _parse_primary()
                                    └── Regex-based parsing
```

### After TASK-060
```
┌──────────────────────────────────────────────────────────┐
│              UnifiedEvaluator (626 lines)                │
│  ┌────────────────────────────────────────────────────┐  │
│  │                   AST Core                          │  │
│  │  - Arithmetic: + - * / // % **                     │  │
│  │  - Math: 22 functions (abs, min, max, sin, etc.)   │  │
│  │  - Comparisons: < <= > >= == !=                    │  │
│  │  - Chained: 0 < x < 10                             │  │
│  │  - Logic: and, or, not                             │  │
│  │  - Ternary: x if cond else y                       │  │
│  │  - Strings: mode == 'EDIT'                         │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
           ▲                         ▲
           │                         │
    ┌──────┴──────┐           ┌──────┴──────┐
    │ Expression  │           │  Condition  │
    │  Evaluator  │           │  Evaluator  │
    │ (246 lines) │           │ (196 lines) │
    │             │           │             │
    │ - $CALCULATE│           │ - fail-open │
    │ - $variable │           │ - simulate_ │
    │ - flatten   │           │   step_     │
    │   context   │           │   effect()  │
    └─────────────┘           └─────────────┘
```

---

## Domain Interface

**File**: `server/router/domain/interfaces/i_expression_evaluator.py`

```python
class IExpressionEvaluator(ABC):
    """Abstract interface for expression evaluation."""

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

---

## UnifiedEvaluator Implementation

**File**: `server/router/application/evaluator/unified_evaluator.py`

### Core Methods

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `evaluate(expr)` | `Any` | Main evaluation (float, str) |
| `evaluate_as_bool(expr)` | `bool` | Boolean coercion |
| `evaluate_as_float(expr)` | `float` | Float coercion |
| `evaluate_safe(expr, default)` | `Any` | Fallback on error |
| `resolve_computed_parameters(params)` | `Dict` | Topological sort |

### Supported Operators

```python
# Arithmetic
2 + 3 * 4           # -> 14.0
10 / 3              # -> 3.333...
10 // 3             # -> 3.0
10 % 3              # -> 1.0
2 ** 10             # -> 1024.0
-5                  # -> -5.0

# Comparisons
x > 5               # -> 1.0 or 0.0
x == 'EDIT'         # -> 1.0 or 0.0 (string comparison)
0 < x < 10          # -> chained comparison

# Logic (short-circuit)
a and b             # -> evaluates b only if a is truthy
a or b              # -> evaluates b only if a is falsy
not a               # -> logical negation

# Ternary
x if condition else y
```

### Math Functions (22)

| Category | Functions |
|----------|-----------|
| Basic | `abs`, `min`, `max`, `round`, `trunc` |
| Rounding | `floor`, `ceil` |
| Powers | `sqrt`, `pow`, `exp`, `log`, `log10` |
| Trigonometry | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2` |
| Angles | `degrees`, `radians` |
| Geometry | `hypot` |

### Security

```python
# BLOCKED (raises ValueError):
__import__('os')
eval('...')
exec('...')
open('/etc/passwd')
```

The evaluator uses Python's `ast.literal_eval` principles with a restricted node whitelist.

---

## Wrapper: ExpressionEvaluator

**File**: `server/router/application/evaluator/expression_evaluator.py`

### Responsibilities Kept
- `$CALCULATE(expr)` pattern matching
- `$variable` direct references
- Context flattening (`dimensions` → `width`, `height`, `depth`)
- Recursive parameter resolution (`resolve_params()` + `resolve_param_value()`)
- Delegation for computed parameters (`resolve_computed_parameters()`)

### Delegation

```python
def evaluate(self, expression: str) -> Optional[float]:
    """Delegate to UnifiedEvaluator."""
    try:
        return self._unified.evaluate_as_float(expression)
    except Exception:
        return None
```

---

## Wrapper: ConditionEvaluator

**File**: `server/router/application/evaluator/condition_evaluator.py`

### Responsibilities Kept
- Fail-open behavior (returns `True` on error)
- `simulate_step_effect()` for workflow step simulation
- `set_context_from_scene()` adapter for scene inspection

### Delegation

```python
def evaluate(self, condition: str) -> bool:
    """Delegate to UnifiedEvaluator."""
    try:
        return self._unified.evaluate_as_bool(condition)
    except Exception:
        return True  # Fail-open
```

---

## New Capabilities

### Math Functions in Conditions (NEW)

```yaml
# Before TASK-060: NOT SUPPORTED
condition: "floor(table_width / plank_width) > 5"  # ERROR

# After TASK-060: WORKS
condition: "floor(table_width / plank_width) > 5"  # -> True/False
condition: "sqrt(width * width + depth * depth) < 2.0"
condition: "ceil(count / 2) == 3"
```

### Ternary in $CALCULATE (NEW)

```yaml
# Before TASK-060: NOT SUPPORTED
value: "$CALCULATE(0.10 if i <= plank_full_count else plank_remainder_width)"

# After TASK-060: WORKS
value: "$CALCULATE(0.10 if i <= plank_full_count else plank_remainder_width)"
value: "$CALCULATE(1 if width > 1.0 else 0)"
```

### Comparisons and Logic in $CALCULATE (NEW)

```yaml
value: "$CALCULATE(10 if a and b else 0)"
value: "$CALCULATE(1 if x > 3 and y < 5 else 2)"
```

---

## Computed Parameter Resolution

The `resolve_computed_parameters()` method uses topological sorting to handle dependencies:

```yaml
parameters:
  base_width:
    value: 1.0
  half_width:
    value: "$CALCULATE(base_width / 2)"  # depends on base_width
  quarter_width:
    value: "$CALCULATE(half_width / 2)"  # depends on half_width
```

Resolution order: `base_width` → `half_width` → `quarter_width`

### Cycle Detection

```yaml
# ERROR: Circular dependency
parameters:
  a:
    value: "$CALCULATE(b + 1)"
  b:
    value: "$CALCULATE(a + 1)"
```

---

## Testing

### Unit Tests

**File**: `tests/unit/router/application/evaluator/test_unified_evaluator.py`

| Test Category | Coverage |
|---------------|----------|
| Arithmetic | `+`, `-`, `*`, `/`, `//`, `%`, `**` |
| Math functions | All 22 functions |
| Comparisons | `<`, `<=`, `>`, `>=`, `==`, `!=` |
| Chained comparisons | `0 < x < 10` |
| Logical operators | `and`, `or`, `not` with precedence |
| Ternary | `x if cond else y` |
| String comparisons | `mode == 'EDIT'` |
| Boolean literals | `True`, `False` |
| Computed parameters | Dependency resolution |
| Topological sort | Cycle detection |
| Security | Import/eval/exec blocking |

### Backward Compatibility

All 279 existing evaluator tests pass unchanged:
- `test_expression_evaluator.py` - ✅
- `test_expression_evaluator_extended.py` - ✅
- `test_condition_evaluator.py` - ✅
- `test_condition_evaluator_parentheses.py` - ✅
- `test_proportion_resolver.py` - ✅

---

## Architecture Decisions

### Why Domain Interface?

1. **Clean Architecture Compliance**: All router components have interfaces
2. **Dependency Inversion**: High-level modules depend on abstractions
3. **Testability**: Allows mocking in unit tests

### Why Keep Wrappers?

1. **Separation of Concerns**: Each wrapper has domain-specific responsibilities
2. **Backward Compatibility**: Existing code continues to work
3. **Single Responsibility**: UnifiedEvaluator handles only math/logic

### Why `Any` Return Type?

1. **String Comparisons**: `mode == 'EDIT'` needs string handling
2. **Flexibility**: Different callers need different types
3. **Type Safety at Wrapper Level**: `evaluate_as_bool()`, `evaluate_as_float()`

---

## Related Documentation

- [25-expression-evaluator.md](./25-expression-evaluator.md) - Original expression evaluator
- [26-condition-evaluator.md](./26-condition-evaluator.md) - Original condition evaluator
- [33-parametric-variables.md](./33-parametric-variables.md) - Parametric workflow system
- [Changelog 108](../../_CHANGELOG/108-2025-12-12-unified-expression-evaluator.md) - Full changelog

---

## Files

| File | Lines | Change |
|------|-------|--------|
| `i_expression_evaluator.py` | 97 | NEW |
| `unified_evaluator.py` | 626 | NEW |
| `expression_evaluator.py` | 246 | Refactored (was ~466) |
| `condition_evaluator.py` | 196 | Refactored (was ~383) |
| `test_unified_evaluator.py` | ~400 | NEW |
