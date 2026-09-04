# 85 - Expression Evaluator (TASK-041 P2)

**Date:** 2025-12-03
**Version:** -
**Task:** TASK-041-7, TASK-041-8, TASK-041-9

---

## Summary

Implemented Phase P2 of TASK-041 (Router YAML Workflow Integration) - the Expression Evaluator system that enables dynamic parameter calculation in workflow definitions using `$CALCULATE(...)` expressions.

---

## Changes

### New Files

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/__init__.py` | Module init with exports |
| `server/router/application/evaluator/expression_evaluator.py` | Safe AST-based expression evaluator |
| `tests/unit/router/application/evaluator/__init__.py` | Test module init |
| `tests/unit/router/application/evaluator/test_expression_evaluator.py` | 48 comprehensive tests |

### Modified Files

| File | Change |
|------|--------|
| `server/router/application/workflows/registry.py` | Integrated ExpressionEvaluator for parameter resolution |
| `server/router/application/router.py` | Added `_build_eval_context()` to pass scene context |

---

## Features

### 1. ExpressionEvaluator Class

Safe expression evaluator that supports:

**Arithmetic Operations:**
- Addition, subtraction, multiplication, division
- Power (`**`), modulo (`%`), floor division (`//`)
- Unary plus and minus

**Math Functions (whitelist):**
- `abs()`, `min()`, `max()`, `round()`
- `floor()`, `ceil()`, `sqrt()`

**Variable References:**
- `width`, `height`, `depth` (from scene dimensions)
- `min_dim`, `max_dim` (calculated from dimensions)
- `proportions_*` (flattened from proportions dict)
- Custom parameters from workflow

**Security:**
- AST-based parsing (no `eval()`)
- Whitelist-only function calls
- No imports, attribute access, or subscripting allowed

### 2. $CALCULATE(...) Syntax

```yaml
steps:
  - tool: mesh_bevel
    params:
      width: "$CALCULATE(min_dim * 0.05)"  # 5% of smallest dimension
      segments: 3
```

### 3. Simple Variable References

```yaml
steps:
  - tool: mesh_extrude_region
    params:
      move: [0, 0, "$depth"]  # Uses scene depth directly
```

### 4. Scene Context Integration

The router now passes scene context to workflow expansion:
- Active object dimensions
- Proportions data
- Selection/topology info
- Current mode

---

## Code Examples

### Expression Evaluation

```python
from server.router.application.evaluator import ExpressionEvaluator

evaluator = ExpressionEvaluator()
evaluator.set_context({"width": 2.0, "height": 4.0, "depth": 0.5})

# Basic arithmetic
evaluator.evaluate("width * 0.5")  # -> 1.0
evaluator.evaluate("height / width")  # -> 2.0

# Math functions
evaluator.evaluate("min(width, height, depth)")  # -> 0.5
evaluator.evaluate("sqrt(width)")  # -> 1.414...

# Complex expressions
evaluator.evaluate("(width + height) * depth")  # -> 3.0
```

### Parameter Resolution

```python
# Resolve $CALCULATE expressions
evaluator.resolve_param_value("$CALCULATE(min_dim * 0.05)")  # -> 0.025

# Resolve simple variables
evaluator.resolve_param_value("$depth")  # -> 0.5

# Non-expressions pass through
evaluator.resolve_param_value("CUBE")  # -> "CUBE"
evaluator.resolve_param_value(42)  # -> 42
```

### WorkflowRegistry Integration

```python
from server.router.application.workflows.registry import get_workflow_registry

registry = get_workflow_registry()

# Context is now passed to expand_workflow
calls = registry.expand_workflow(
    "phone_workflow",
    params={"base_depth": 0.1},
    context={
        "dimensions": [2.0, 4.0, 0.5],
        "mode": "OBJECT",
    }
)
```

---

## Testing

**48 tests added** covering:
- Initialization and context setup
- Basic arithmetic operations
- Math functions (nested calls)
- Parameter resolution ($CALCULATE, $variable)
- Safety (no imports, eval, exec, attribute access)
- Edge cases (empty, syntax errors, division by zero)
- Real-world workflow examples

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/ -v
```

---

## Architecture

```
server/router/application/
├── evaluator/
│   ├── __init__.py
│   └── expression_evaluator.py   # NEW
├── workflows/
│   └── registry.py               # MODIFIED - uses evaluator
└── router.py                     # MODIFIED - builds eval context
```

### Data Flow

```
User calls tool
       │
       ▼
SupervisorRouter.process_llm_tool_call()
       │
       ├── _check_workflow_trigger()
       │       │
       │       ▼
       │   _expand_triggered_workflow()
       │       │
       │       ├── _build_eval_context()  ← Scene data
       │       │
       │       ▼
       │   WorkflowRegistry.expand_workflow(context=...)
       │       │
       │       ▼
       │   ExpressionEvaluator.set_context()
       │       │
       │       ▼
       │   _resolve_single_value() for each param
       │       │
       │       ├── $CALCULATE(...) → evaluator.evaluate()
       │       └── $variable → context lookup
       │
       ▼
   Workflow steps with resolved numeric params
```

---

## YAML Workflow Example

```yaml
name: phone_with_dynamic_params
description: Phone with calculated parameters
trigger_keywords: ["phone", "smartphone"]

steps:
  - tool: modeling_create_primitive
    params: { type: "CUBE" }

  - tool: modeling_transform_object
    params:
      scale:
        - "$CALCULATE(width * 0.9)"
        - "$CALCULATE(height * 0.9)"
        - "$depth"

  - tool: system_set_mode
    params: { mode: "EDIT" }

  - tool: mesh_bevel
    params:
      width: "$CALCULATE(min_dim * 0.05)"
      segments: 3

  - tool: mesh_inset
    params:
      thickness: "$CALCULATE(min_dim * 0.03)"
```

---

## Next Steps (P3)

- **TASK-041-10**: Create ConditionEvaluator for `condition` field in steps
- **TASK-041-11**: Integrate into workflow execution (skip steps based on conditions)
- **TASK-041-12**: Update context during workflow execution (simulated mode changes)
