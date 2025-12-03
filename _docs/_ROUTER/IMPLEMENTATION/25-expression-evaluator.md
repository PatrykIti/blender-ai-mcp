# 25 - Expression Evaluator

**Task:** TASK-041-7, TASK-041-8, TASK-041-9
**Phase:** P2
**Status:** ✅ Complete

---

## Overview

The Expression Evaluator enables dynamic parameter calculation in YAML workflows. Instead of hardcoding values, workflow authors can use `$CALCULATE(...)` expressions that are evaluated at runtime based on scene context.

---

## Problem Statement

YAML workflows had static parameter values:

```yaml
steps:
  - tool: mesh_bevel
    params:
      width: 0.05  # Hardcoded - doesn't adapt to object size
```

This doesn't work for different object sizes. A bevel of 0.05 looks good on a 1m cube but is invisible on a 10m cube.

---

## Solution

Dynamic expressions that calculate values from scene context:

```yaml
steps:
  - tool: mesh_bevel
    params:
      width: "$CALCULATE(min_dim * 0.05)"  # 5% of smallest dimension
```

---

## Implementation

### Files Created

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/__init__.py` | Module exports |
| `server/router/application/evaluator/expression_evaluator.py` | Core evaluator |

### Files Modified

| File | Change |
|------|--------|
| `server/router/application/workflows/registry.py` | Added evaluator integration |
| `server/router/application/router.py` | Added `_build_eval_context()` |

---

## ExpressionEvaluator Class

### Initialization

```python
from server.router.application.evaluator import ExpressionEvaluator

evaluator = ExpressionEvaluator()
```

### Setting Context

Context can come from scene data, tool parameters, or both:

```python
# From dimensions array
evaluator.set_context({"dimensions": [2.0, 4.0, 0.5]})
# Automatically creates: width=2.0, height=4.0, depth=0.5, min_dim=0.5, max_dim=4.0

# Direct values
evaluator.set_context({"width": 2.0, "height": 4.0, "depth": 0.5})

# Proportions (flattened with prefix)
evaluator.set_context({
    "proportions": {
        "aspect_xy": 0.5,
        "is_flat": True,
    }
})
# Creates: proportions_aspect_xy=0.5, proportions_is_flat=1.0
```

### Evaluating Expressions

```python
# Basic arithmetic
evaluator.evaluate("2 + 3")  # -> 5.0
evaluator.evaluate("width * 0.5")  # -> 1.0
evaluator.evaluate("height / width")  # -> 2.0

# Math functions
evaluator.evaluate("min(width, height, depth)")  # -> 0.5
evaluator.evaluate("max(2, 3)")  # -> 3.0
evaluator.evaluate("abs(-5)")  # -> 5.0
evaluator.evaluate("sqrt(4)")  # -> 2.0
evaluator.evaluate("floor(3.7)")  # -> 3.0
evaluator.evaluate("ceil(3.2)")  # -> 4.0
evaluator.evaluate("round(3.5)")  # -> 4.0

# Complex expressions
evaluator.evaluate("(width + height) * depth")  # -> 3.0
evaluator.evaluate("min(abs(-5), max(2, 3))")  # -> 3.0
```

### Resolving Parameter Values

```python
# $CALCULATE(...) expressions
evaluator.resolve_param_value("$CALCULATE(width * 0.1)")  # -> 0.2

# Simple $variable references
evaluator.resolve_param_value("$width")  # -> 2.0

# Non-expressions pass through
evaluator.resolve_param_value("CUBE")  # -> "CUBE"
evaluator.resolve_param_value(42)  # -> 42
evaluator.resolve_param_value(None)  # -> None
```

### Batch Resolution

```python
params = {
    "size": "$CALCULATE(width * 0.5)",
    "mode": "EDIT",
    "count": 5,
    "scale": [1.0, "$CALCULATE(height / 2)", "$depth"],
    "nested": {"inner": "$CALCULATE(width + 1)"},
}

resolved = evaluator.resolve_params(params)
# {
#     "size": 1.0,
#     "mode": "EDIT",
#     "count": 5,
#     "scale": [1.0, 2.0, 0.5],
#     "nested": {"inner": 3.0},
# }
```

---

## Safety Features

The evaluator uses AST parsing instead of `eval()` to prevent arbitrary code execution.

### Allowed Operations

| Category | Allowed |
|----------|---------|
| **Arithmetic** | `+`, `-`, `*`, `/`, `**`, `%`, `//` |
| **Unary** | `+x`, `-x` |
| **Functions** | `abs`, `min`, `max`, `round`, `floor`, `ceil`, `sqrt` |
| **Constants** | Numbers (int, float) |
| **Variables** | From context only |

### Blocked Operations

All of these return `None`:

```python
# No imports
evaluator.evaluate("__import__('os')")  # -> None

# No eval/exec
evaluator.evaluate("eval('1+1')")  # -> None
evaluator.evaluate("exec('x=1')")  # -> None

# No attribute access
evaluator.evaluate("'string'.upper()")  # -> None

# No subscripts
evaluator.evaluate("[1,2,3][0]")  # -> None

# No arbitrary functions
evaluator.evaluate("open('file.txt')")  # -> None
evaluator.evaluate("print('hello')")  # -> None
```

---

## WorkflowRegistry Integration

### Expand Workflow with Context

```python
from server.router.application.workflows.registry import get_workflow_registry

registry = get_workflow_registry()

# Context enables $CALCULATE expressions
calls = registry.expand_workflow(
    workflow_name="phone_workflow",
    params={"base_depth": 0.1},
    context={
        "dimensions": [2.0, 4.0, 0.5],
        "mode": "OBJECT",
        "proportions": {"is_flat": True},
    }
)
```

### Parameter Resolution in Steps

The registry's `_resolve_single_value()` method handles:

1. **List values**: Resolves each element recursively
2. **Dict values**: Resolves nested dictionaries
3. **$CALCULATE(...)**: Evaluates expression
4. **$variable**: Looks up in params, then context
5. **Plain values**: Returns as-is

---

## SupervisorRouter Integration

### Building Evaluation Context

The router's `_build_eval_context()` method collects:

```python
def _build_eval_context(self, context: SceneContext, params: Dict) -> Dict:
    eval_context = {"mode": context.mode}

    # Tool parameters
    if params:
        eval_context.update(params)

    # Active object dimensions
    active_dims = context.get_active_dimensions()
    if active_dims:
        eval_context["dimensions"] = active_dims
        eval_context["width"] = active_dims[0]
        eval_context["height"] = active_dims[1]
        eval_context["depth"] = active_dims[2]
        eval_context["min_dim"] = min(active_dims[:3])
        eval_context["max_dim"] = max(active_dims[:3])

    # Proportions
    if context.proportions:
        eval_context["proportions"] = context.proportions.to_dict()
        # Flatten with prefix
        for key, value in context.proportions.to_dict().items():
            if isinstance(value, (int, float)):
                eval_context[f"proportions_{key}"] = value

    # Topology/selection
    if context.topology:
        eval_context["selected_verts"] = context.topology.selected_verts
        eval_context["selected_edges"] = context.topology.selected_edges
        eval_context["selected_faces"] = context.topology.selected_faces
        eval_context["has_selection"] = context.topology.has_selection

    return eval_context
```

### Pipeline Flow

```
process_llm_tool_call()
       │
       ▼
_check_workflow_trigger()
       │
       ▼
_expand_triggered_workflow(workflow_name, params, context)
       │
       ├── _build_eval_context(context, params)
       │
       ▼
registry.expand_workflow(name, params, eval_context)
       │
       ▼
ExpressionEvaluator resolves all $CALCULATE and $variable
       │
       ▼
Workflow steps with numeric values
```

---

## Testing

### Test Structure

```
tests/unit/router/application/evaluator/
├── __init__.py
└── test_expression_evaluator.py
```

### Test Classes

| Class | Tests |
|-------|-------|
| `TestExpressionEvaluatorInit` | Context setup |
| `TestBasicArithmetic` | +, -, *, /, **, %, // |
| `TestMathFunctions` | abs, min, max, round, floor, ceil, sqrt |
| `TestResolveParamValue` | $CALCULATE, $variable, passthrough |
| `TestResolveParams` | Batch resolution, lists, nested dicts |
| `TestSafety` | Blocked operations |
| `TestEdgeCases` | Empty, syntax errors, division by zero |
| `TestRealWorldExamples` | Actual workflow scenarios |

### Running Tests

```bash
# All evaluator tests
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/ -v

# Quick check
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/ -v --tb=short
```

---

## YAML Workflow Examples

### Phone Workflow with Dynamic Params

```yaml
name: phone_dynamic
description: Phone with calculated screen depth
trigger_keywords: ["phone", "smartphone"]

steps:
  - tool: modeling_create_primitive
    params:
      type: CUBE

  - tool: system_set_mode
    params:
      mode: EDIT

  - tool: mesh_select
    params:
      action: all

  - tool: mesh_bevel
    params:
      width: "$CALCULATE(min_dim * 0.05)"
      segments: 3

  - tool: mesh_inset
    params:
      thickness: "$CALCULATE(min_dim * 0.03)"

  - tool: mesh_extrude_region
    params:
      move: [0, 0, "$CALCULATE(-depth * 0.5)"]
```

### Scale Calculation

```yaml
steps:
  - tool: modeling_transform_object
    params:
      scale:
        - "$CALCULATE(width * 0.8)"
        - "$CALCULATE(height * 0.8)"
        - "$CALCULATE(depth * 0.8)"
```

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid expression | Returns `None`, logs warning |
| Unknown variable | Returns `None`, logs warning |
| Division by zero | Returns `None`, logs warning |
| Blocked operation | Returns `None`, logs warning |
| $CALCULATE fails | Returns original string |
| $variable not found | Returns original string |

All errors fail gracefully without raising exceptions.

---

## Performance Considerations

- AST parsing is done per expression (not cached)
- Context is set once per workflow expansion
- Variable substitution uses regex (efficient for typical workflows)
- No external dependencies beyond standard library

---

## Future Enhancements

For P3 (Condition Evaluator):
- Boolean comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Logical operators: `and`, `or`, `not`
- String comparisons: `mode == 'EDIT'`

For P4 (Proportion Resolver):
- `$AUTO_BEVEL`: 5% of smallest dimension
- `$AUTO_INSET`: 3% of face area
- `$AUTO_EXTRUDE`: 10% of height
