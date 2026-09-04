# 87 - Proportion Resolver (TASK-041 P4)

**Date:** 2025-12-03
**Version:** -
**Task:** TASK-041-13, TASK-041-14

---

## Summary

Implemented Phase P4 of TASK-041 (Router YAML Workflow Integration) - the ProportionResolver that enables `$AUTO_*` parameters in workflow definitions. These parameters automatically calculate values based on object dimensions, enabling workflows to work well regardless of object scale.

---

## Changes

### New Files

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/proportion_resolver.py` | Dimension-relative parameter resolver |
| `tests/unit/router/application/evaluator/test_proportion_resolver.py` | 42 tests for ProportionResolver |
| `tests/unit/router/application/workflows/test_registry_proportions.py` | 6 integration tests |

### Modified Files

| File | Change |
|------|--------|
| `server/router/application/evaluator/__init__.py` | Export ProportionResolver |
| `server/router/application/workflows/registry.py` | Integrated $AUTO_* resolution |

---

## Features

### Available $AUTO_* Parameters

| Parameter | Calculation | Description |
|-----------|-------------|-------------|
| `$AUTO_BEVEL` | `min(dims) * 0.05` | 5% of smallest dimension |
| `$AUTO_BEVEL_SMALL` | `min(dims) * 0.02` | 2% of smallest dimension |
| `$AUTO_BEVEL_LARGE` | `min(dims) * 0.10` | 10% of smallest dimension |
| `$AUTO_INSET` | `min(x, y) * 0.03` | 3% of XY plane smallest |
| `$AUTO_INSET_THICK` | `min(x, y) * 0.05` | 5% of XY plane smallest |
| `$AUTO_EXTRUDE` | `z * 0.10` | 10% of Z height |
| `$AUTO_EXTRUDE_SMALL` | `z * 0.05` | 5% of Z height |
| `$AUTO_EXTRUDE_DEEP` | `z * 0.20` | 20% of Z height |
| `$AUTO_EXTRUDE_NEG` | `-z * 0.10` | Inward 10% of Z |
| `$AUTO_SCALE_SMALL` | `[x*0.8, y*0.8, z*0.8]` | 80% of each dimension |
| `$AUTO_SCALE_TINY` | `[x*0.5, y*0.5, z*0.5]` | 50% of each dimension |
| `$AUTO_OFFSET` | `min(dims) * 0.02` | 2% of smallest |
| `$AUTO_THICKNESS` | `z * 0.05` | 5% of Z |
| `$AUTO_SCREEN_DEPTH` | `z * 0.50` | 50% of Z (phone screens) |
| `$AUTO_SCREEN_DEPTH_NEG` | `-z * 0.50` | Inward 50% of Z |
| `$AUTO_LOOP_POS` | `0.8` | Loop cut position factor |

---

## Code Examples

### Basic Usage

```python
from server.router.application.evaluator import ProportionResolver

resolver = ProportionResolver()
resolver.set_dimensions([2.0, 4.0, 0.5])  # [width, height, depth]

# Resolve AUTO params
resolver.resolve("$AUTO_BEVEL")       # -> 0.025 (5% of 0.5)
resolver.resolve("$AUTO_INSET")       # -> 0.06 (3% of 2.0)
resolver.resolve("$AUTO_EXTRUDE_NEG") # -> -0.05 (10% of 0.5)

# Scale returns a list
resolver.resolve("$AUTO_SCALE_SMALL") # -> [1.6, 3.2, 0.4]
```

### Batch Resolution

```python
params = {
    "width": "$AUTO_BEVEL",
    "segments": 3,
    "move": [0, 0, "$AUTO_EXTRUDE_NEG"],
}

resolved = resolver.resolve_params(params)
# {
#     "width": 0.025,
#     "segments": 3,
#     "move": [0, 0, -0.05],
# }
```

### Workflow Integration

```python
from server.router.application.workflows.registry import get_workflow_registry

registry = get_workflow_registry()

# Dimensions from context enable AUTO params
context = {
    "dimensions": [0.07, 0.15, 0.008],  # Phone dimensions
    "mode": "OBJECT",
}

calls = registry.expand_workflow("phone_workflow", context=context)
# $AUTO_* params are resolved based on phone dimensions
```

---

## YAML Workflow Example

```yaml
name: smart_phone_workflow
description: Phone with auto-calculated dimensions
trigger_keywords: ["phone", "smartphone"]

steps:
  - tool: modeling_create_primitive
    params:
      type: CUBE

  - tool: system_set_mode
    params:
      mode: EDIT
    condition: "current_mode != 'EDIT'"

  - tool: mesh_select
    params:
      action: all

  # Bevel adapts to object size
  - tool: mesh_bevel
    params:
      width: "$AUTO_BEVEL"      # 5% of smallest dim
      segments: 3

  # Inset adapts to face size
  - tool: mesh_inset
    params:
      thickness: "$AUTO_INSET"  # 3% of XY smallest

  # Screen depth adapts to phone thickness
  - tool: mesh_extrude_region
    params:
      move: [0, 0, "$AUTO_SCREEN_DEPTH_NEG"]  # 50% of depth inward
```

---

## Testing

**48 new tests added:**
- 42 tests for ProportionResolver
- 6 integration tests for WorkflowRegistry

```bash
# Run ProportionResolver tests
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/test_proportion_resolver.py -v

# Run registry integration tests
PYTHONPATH=. poetry run pytest tests/unit/router/application/workflows/test_registry_proportions.py -v
```

---

## Architecture

```
server/router/application/
├── evaluator/
│   ├── __init__.py
│   ├── expression_evaluator.py   # P2 - $CALCULATE
│   ├── condition_evaluator.py    # P3 - condition field
│   └── proportion_resolver.py    # P4 - $AUTO_* (NEW)
└── workflows/
    └── registry.py               # MODIFIED - uses ProportionResolver
```

### Resolution Order in WorkflowRegistry

```
_resolve_single_value(value)
       │
       ├── Is list? → Resolve each element recursively
       ├── Is dict? → Resolve each value recursively
       │
       ├── Starts with "$CALCULATE("? → ExpressionEvaluator
       ├── Starts with "$AUTO_"? → ProportionResolver (NEW)
       ├── Starts with "$"? → Simple variable lookup
       │
       └── Return as-is
```

---

## Real-World Results

### Phone Workflow (7cm × 15cm × 8mm)

| Parameter | $AUTO_* | Resolved |
|-----------|---------|----------|
| Bevel width | `$AUTO_BEVEL` | 0.4mm |
| Inset thickness | `$AUTO_INSET` | 2.1mm |
| Screen depth | `$AUTO_SCREEN_DEPTH_NEG` | -4mm |

### Table Workflow (1.2m × 0.8m × 0.75m)

| Parameter | $AUTO_* | Resolved |
|-----------|---------|----------|
| Edge bevel | `$AUTO_BEVEL` | 37.5mm |
| Leg extrude | `$AUTO_EXTRUDE` | 75mm |

---

## Fallback Behavior

When dimensions are not available:
- `$AUTO_*` params return unchanged as strings
- Workflow continues without error
- Parameters can be set manually by user

This enables workflows to work even when scene context is incomplete.

---

## Complete TASK-041 Status

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase -1, P0 | Clean Architecture & YAML | ✅ |
| P1 | WorkflowTriggerer Integration | ✅ |
| P2 | Expression Evaluator ($CALCULATE) | ✅ |
| P3 | Condition Evaluator (condition) | ✅ |
| P4 | Proportion Resolver ($AUTO_*) | ✅ |

**TASK-041 is now complete!**
