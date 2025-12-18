# 86 - Condition Evaluator (TASK-041 P3)

**Date:** 2025-12-03
**Version:** -
**Task:** TASK-041-10, TASK-041-11, TASK-041-12

---

## Summary

Implemented Phase P3 of TASK-041 (Router YAML Workflow Integration) - the Condition Evaluator system that enables conditional step execution in workflow definitions using the `condition` field.

---

## Changes

### New Files

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/condition_evaluator.py` | Boolean condition evaluator |
| `tests/unit/router/application/evaluator/test_condition_evaluator.py` | 47 tests for ConditionEvaluator |
| `tests/unit/router/application/workflows/test_registry_conditions.py` | 10 tests for registry integration |

### Modified Files

| File | Change |
|------|--------|
| `server/router/application/evaluator/__init__.py` | Export ConditionEvaluator |
| `server/router/application/workflows/registry.py` | Integrated conditional step execution |

---

## Features

### 1. ConditionEvaluator Class

Boolean condition evaluator that supports:

**Comparison Operators:**
- `==`, `!=` (equality)
- `>`, `<`, `>=`, `<=` (numeric)

**Logical Operators:**
- `not` (prefix negation)
- `and`, `or` (boolean logic)

**Value Types:**
- String literals: `'EDIT'`, `"OBJECT"`
- Numbers: `0`, `5`, `3.14`
- Booleans: `true`, `false`
- Variables: `current_mode`, `has_selection`

### 2. Conditional Steps in YAML

```yaml
steps:
  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"  # Only switch if not in EDIT

  - tool: mesh_select
    params: { action: "all" }
    condition: "not has_selection"  # Only select if nothing selected

  - tool: mesh_subdivide
    params: { number_cuts: 2 }
    condition: "selected_verts >= 4"  # Only if enough vertices
```

### 3. Context Simulation (TASK-041-12)

The evaluator simulates context changes during workflow expansion:
- `system_set_mode` → updates `current_mode`
- `mesh_select all` → sets `has_selection = True`
- `mesh_select none` → sets `has_selection = False`
- `modeling_create_primitive` → increments `object_count`

This prevents redundant steps in workflows with multiple conditional mode switches.

---

## Code Examples

### Basic Condition Evaluation

```python
from server.router.application.evaluator import ConditionEvaluator

evaluator = ConditionEvaluator()
evaluator.set_context({
    "current_mode": "OBJECT",
    "has_selection": False,
    "object_count": 5,
})

# String comparison
evaluator.evaluate("current_mode == 'OBJECT'")  # -> True
evaluator.evaluate("current_mode != 'EDIT'")    # -> True

# Boolean variable
evaluator.evaluate("has_selection")             # -> False
evaluator.evaluate("not has_selection")         # -> True

# Numeric comparison
evaluator.evaluate("object_count > 0")          # -> True
evaluator.evaluate("object_count >= 5")         # -> True

# Logical operators
evaluator.evaluate("current_mode == 'EDIT' and has_selection")  # -> False
evaluator.evaluate("current_mode == 'OBJECT' or has_selection") # -> True
```

### Context Simulation

```python
evaluator = ConditionEvaluator()
evaluator.set_context({"current_mode": "OBJECT", "has_selection": False})

# Before mode switch
evaluator.evaluate("current_mode != 'EDIT'")  # -> True

# Simulate mode switch
evaluator.simulate_step_effect("system_set_mode", {"mode": "EDIT"})

# After mode switch
evaluator.evaluate("current_mode != 'EDIT'")  # -> False (now in EDIT)
```

### Workflow Expansion with Conditions

```python
from server.router.application.workflows.registry import get_workflow_registry

registry = get_workflow_registry()

# Context determines which steps run
context = {
    "mode": "OBJECT",
    "has_selection": False,
}

calls = registry.expand_workflow("phone_workflow", context=context)
# Steps with false conditions are automatically skipped
```

---

## Available Context Variables

| Variable | Type | Source |
|----------|------|--------|
| `current_mode` | str | Scene mode (OBJECT, EDIT, SCULPT) |
| `has_selection` | bool | Whether geometry is selected |
| `selected_verts` | int | Number of selected vertices |
| `selected_edges` | int | Number of selected edges |
| `selected_faces` | int | Number of selected faces |
| `object_count` | int | Number of objects in scene |
| `active_object` | str | Name of active object |

---

## Fail-Open Behavior

The evaluator uses fail-open semantics:
- Unknown variables: condition returns `True` (execute step)
- Parse errors: condition returns `True` (execute step)
- Empty/None condition: always returns `True`

This ensures workflows don't break due to missing context.

---

## Testing

**57 new tests added:**
- 47 tests for ConditionEvaluator
- 10 tests for WorkflowRegistry integration

```bash
# Run condition evaluator tests
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/test_condition_evaluator.py -v

# Run registry condition tests
PYTHONPATH=. poetry run pytest tests/unit/router/application/workflows/test_registry_conditions.py -v
```

---

## Architecture

```
server/router/application/
├── evaluator/
│   ├── __init__.py
│   ├── expression_evaluator.py   # P2 - $CALCULATE
│   └── condition_evaluator.py    # P3 - condition field (NEW)
└── workflows/
    └── registry.py               # MODIFIED - uses ConditionEvaluator
```

### Data Flow

```
expand_workflow()
       │
       ├── _build_condition_context()  ← Extract mode, selection, etc.
       │
       └── _steps_to_calls()
               │
               ├── For each step:
               │   ├── Check condition with ConditionEvaluator
               │   │       │
               │   │       ├── True → Add to calls
               │   │       └── False → Skip step
               │   │
               │   └── Simulate step effect (update context)
               │
               └── Return filtered calls
```

---

## YAML Workflow Example

```yaml
name: smart_phone_workflow
description: Phone workflow with intelligent conditionals
trigger_keywords: ["phone", "smartphone"]

steps:
  # Only switch mode if needed
  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"

  # Only select if nothing selected
  - tool: mesh_select
    params: { action: "all" }
    condition: "not has_selection"

  # Always run bevel
  - tool: mesh_bevel
    params:
      width: "$CALCULATE(min_dim * 0.05)"
      segments: 3

  # Only inset if in EDIT mode (will be true after first step)
  - tool: mesh_inset
    params:
      thickness: "$CALCULATE(min_dim * 0.03)"
    condition: "current_mode == 'EDIT'"

  # Complex condition
  - tool: mesh_extrude_region
    params:
      move: [0, 0, "$CALCULATE(-depth * 0.5)"]
    condition: "current_mode == 'EDIT' and has_selection"
```

---

## Next Steps (P4)

- **TASK-041-13**: Create ProportionResolver for `$AUTO_*` parameters
- **TASK-041-14**: Integrate ProportionResolver into workflows
