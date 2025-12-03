# 26 - Condition Evaluator

**Task:** TASK-041-10, TASK-041-11, TASK-041-12
**Phase:** P3
**Status:** ✅ Complete

---

## Overview

The Condition Evaluator enables conditional step execution in YAML workflows. Steps can specify a `condition` field that determines whether they should execute based on the current scene context.

---

## Problem Statement

Workflows often have redundant steps:

```yaml
steps:
  - tool: system_set_mode
    params: { mode: "EDIT" }
    # Always runs - even if already in EDIT mode!

  - tool: mesh_select
    params: { action: "all" }
    # Always runs - even if geometry is already selected!
```

This causes:
- Unnecessary Blender operations
- Potential errors (e.g., "already in EDIT mode")
- Inefficient workflow execution

---

## Solution

Conditional steps that check context before execution:

```yaml
steps:
  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"  # Only if not already in EDIT

  - tool: mesh_select
    params: { action: "all" }
    condition: "not has_selection"  # Only if nothing selected
```

---

## Implementation

### Files Created

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/condition_evaluator.py` | Core evaluator |
| `tests/unit/router/application/evaluator/test_condition_evaluator.py` | Unit tests |
| `tests/unit/router/application/workflows/test_registry_conditions.py` | Integration tests |

### Files Modified

| File | Change |
|------|--------|
| `server/router/application/evaluator/__init__.py` | Export ConditionEvaluator |
| `server/router/application/workflows/registry.py` | Integrate condition checking |

---

## ConditionEvaluator Class

### Initialization

```python
from server.router.application.evaluator import ConditionEvaluator

evaluator = ConditionEvaluator()
```

### Setting Context

```python
evaluator.set_context({
    "current_mode": "OBJECT",
    "has_selection": False,
    "object_count": 5,
    "selected_verts": 0,
    "selected_faces": 0,
})
```

Or from a SceneContext object:

```python
evaluator.set_context_from_scene(scene_context)
```

### Evaluating Conditions

```python
# String comparisons
evaluator.evaluate("current_mode == 'EDIT'")     # False
evaluator.evaluate("current_mode != 'EDIT'")     # True
evaluator.evaluate("active_object == 'Cube'")    # depends on context

# Boolean variables
evaluator.evaluate("has_selection")              # False
evaluator.evaluate("not has_selection")          # True

# Numeric comparisons
evaluator.evaluate("object_count > 0")           # True
evaluator.evaluate("selected_verts >= 4")        # False
evaluator.evaluate("selected_faces == 0")        # True

# Logical operators
evaluator.evaluate("current_mode == 'EDIT' and has_selection")  # False
evaluator.evaluate("object_count > 0 or has_selection")         # True
evaluator.evaluate("not current_mode == 'SCULPT'")              # True
```

---

## Supported Syntax

### Comparison Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `==` | `mode == 'EDIT'` | Equal |
| `!=` | `mode != 'EDIT'` | Not equal |
| `>` | `count > 0` | Greater than |
| `<` | `count < 10` | Less than |
| `>=` | `count >= 5` | Greater or equal |
| `<=` | `count <= 5` | Less or equal |

### Logical Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `not` | `not has_selection` | Negation |
| `and` | `mode == 'EDIT' and has_selection` | Both true |
| `or` | `mode == 'OBJECT' or no_objects` | Either true |

### Value Types

| Type | Examples | Notes |
|------|----------|-------|
| String | `'EDIT'`, `"OBJECT"` | Single or double quotes |
| Number | `0`, `5`, `3.14` | Int or float |
| Boolean | `true`, `false` | Case insensitive |
| Variable | `current_mode`, `has_selection` | From context |

---

## Context Variables

### Standard Variables

| Variable | Type | Description |
|----------|------|-------------|
| `current_mode` | str | Current Blender mode (OBJECT, EDIT, SCULPT) |
| `has_selection` | bool | Whether any geometry is selected |
| `object_count` | int | Number of objects in scene |
| `active_object` | str | Name of active object |

### Topology Variables

| Variable | Type | Description |
|----------|------|-------------|
| `selected_verts` | int | Number of selected vertices |
| `selected_edges` | int | Number of selected edges |
| `selected_faces` | int | Number of selected faces |
| `total_verts` | int | Total vertex count |
| `total_edges` | int | Total edge count |
| `total_faces` | int | Total face count |

---

## Context Simulation (TASK-041-12)

The evaluator simulates the effect of steps on context to enable accurate condition evaluation within a workflow.

### Simulated Effects

```python
# Mode changes
evaluator.simulate_step_effect("system_set_mode", {"mode": "EDIT"})
# -> current_mode = "EDIT"

# Selection changes
evaluator.simulate_step_effect("mesh_select", {"action": "all"})
# -> has_selection = True

evaluator.simulate_step_effect("mesh_select", {"action": "none"})
# -> has_selection = False

# Object creation
evaluator.simulate_step_effect("modeling_create_primitive", {"type": "CUBE"})
# -> object_count += 1

# Object deletion
evaluator.simulate_step_effect("scene_delete_object", {"name": "Cube"})
# -> object_count -= 1 (if > 0)
```

### Example: Redundant Step Prevention

```yaml
steps:
  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"  # Runs first time

  - tool: mesh_select
    params: { action: "all" }
    condition: "not has_selection"  # Runs

  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"  # SKIPPED - simulation shows EDIT

  - tool: mesh_select
    params: { action: "all" }
    condition: "not has_selection"  # SKIPPED - simulation shows selected
```

---

## WorkflowRegistry Integration

### Condition Context Building

```python
def _build_condition_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and normalize context for condition evaluation."""
    condition_context = {}

    # Mode
    if "mode" in context:
        condition_context["current_mode"] = context["mode"]

    # Selection
    if "has_selection" in context:
        condition_context["has_selection"] = context["has_selection"]
    elif "selected_verts" in context:
        condition_context["has_selection"] = context["selected_verts"] > 0

    # ... more context variables

    return condition_context
```

### Step Filtering

```python
def _steps_to_calls(self, steps, workflow_name):
    calls = []

    for i, step in enumerate(steps):
        # Check condition
        if step.condition:
            should_execute = self._condition_evaluator.evaluate(step.condition)
            if not should_execute:
                logger.debug(f"Skipping step: condition not met")
                continue

        # Create call
        calls.append(CorrectedToolCall(...))

        # Simulate effect for next conditions
        self._condition_evaluator.simulate_step_effect(step.tool, step.params)

    return calls
```

---

## Fail-Open Behavior

The evaluator uses fail-open semantics to prevent workflow breakage:

| Scenario | Result | Reason |
|----------|--------|--------|
| Unknown variable | `True` | Execute step if can't evaluate |
| Parse error | `True` | Don't skip due to syntax issues |
| Empty condition | `True` | No condition = always execute |
| `None` condition | `True` | Same as empty |

### Implications

```python
# Unknown variable
evaluator.evaluate("unknown_var")  # -> True (fail-open)

# But with 'not':
evaluator.evaluate("not unknown_var")  # -> False (not True)
```

---

## Testing

### ConditionEvaluator Tests (47)

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/test_condition_evaluator.py -v
```

Test classes:
- `TestConditionEvaluatorInit` - Initialization and context
- `TestEqualityComparisons` - ==, !=
- `TestNumericComparisons` - >, <, >=, <=
- `TestBooleanVariables` - Direct variable evaluation
- `TestLogicalOperators` - and, or, not
- `TestLiteralValues` - true, false parsing
- `TestEdgeCases` - Empty, unknown, malformed
- `TestSimulateStepEffect` - Context simulation
- `TestRealWorldConditions` - Workflow scenarios

### Registry Integration Tests (10)

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/workflows/test_registry_conditions.py -v
```

Test classes:
- `TestRegistryConditionEvaluation` - Basic condition filtering
- `TestContextSimulation` - Redundant step prevention
- `TestNumericConditions` - Numeric comparisons
- `TestLogicalConditions` - and/or operators

---

## Common Patterns

### Mode Guard

```yaml
- tool: system_set_mode
  params: { mode: "EDIT" }
  condition: "current_mode != 'EDIT'"
```

### Selection Guard

```yaml
- tool: mesh_select
  params: { action: "all" }
  condition: "not has_selection"
```

### Object Exists Guard

```yaml
- tool: scene_delete_object
  params: { name: "Cube" }
  condition: "object_count > 0"
```

### Edit Mode + Selection

```yaml
- tool: mesh_extrude_region
  params: { move: [0, 0, 1] }
  condition: "current_mode == 'EDIT' and has_selection"
```

### Minimum Selection

```yaml
- tool: mesh_subdivide
  params: { number_cuts: 2 }
  condition: "selected_verts >= 4"
```

---

## Limitations

1. **Simple parsing**: No parentheses support (left-to-right evaluation)
2. **No nested conditions**: Can't do `(A or B) and C`
3. **String-only conditions**: Condition field must be a string
4. **Simulation limitations**: Only common tools are simulated

---

## Future Enhancements

- Parentheses support for complex conditions
- More simulation effects (subdivide, extrude, etc.)
- Condition variables in $CALCULATE expressions
