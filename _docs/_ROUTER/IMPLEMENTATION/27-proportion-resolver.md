# 27 - Proportion Resolver

**Task:** TASK-041-13, TASK-041-14
**Phase:** P4
**Status:** ✅ Complete

---

## Overview

The Proportion Resolver enables `$AUTO_*` parameters in YAML workflows. These parameters automatically calculate appropriate values based on object dimensions, allowing workflows to work well regardless of object scale.

---

## Problem Statement

Hardcoded parameter values don't scale well:

```yaml
steps:
  - tool: mesh_bevel
    params:
      offset: 0.05  # Good for 1m cube, invisible on 10m cube, huge on 1cm cube
```

Different object sizes need different values for the same operation.

---

## Solution

Smart defaults that calculate values from object dimensions:

```yaml
steps:
  - tool: mesh_bevel
    params:
      offset: "$AUTO_BEVEL"  # Always 5% of smallest dimension
```

---

## Implementation

### Files Created

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/proportion_resolver.py` | Core resolver |
| `tests/unit/router/application/evaluator/test_proportion_resolver.py` | Unit tests |
| `tests/unit/router/application/workflows/test_registry_proportions.py` | Integration tests |

### Files Modified

| File | Change |
|------|--------|
| `server/router/application/evaluator/__init__.py` | Export ProportionResolver |
| `server/router/application/workflows/registry.py` | Integrate $AUTO_* resolution |

---

## ProportionResolver Class

### Initialization

```python
from server.router.application.evaluator import ProportionResolver

resolver = ProportionResolver()
```

### Setting Dimensions

```python
# Set from list
resolver.set_dimensions([2.0, 4.0, 0.5])  # [width, height, depth]

# Get current dimensions
dims = resolver.get_dimensions()  # [2.0, 4.0, 0.5]

# Clear dimensions
resolver.clear_dimensions()
```

### Resolving Values

```python
resolver.set_dimensions([2.0, 4.0, 0.5])  # min=0.5, XY min=2.0, Z=0.5

# Bevel params
resolver.resolve("$AUTO_BEVEL")       # -> 0.025 (5% of 0.5)
resolver.resolve("$AUTO_BEVEL_SMALL") # -> 0.01 (2% of 0.5)
resolver.resolve("$AUTO_BEVEL_LARGE") # -> 0.05 (10% of 0.5)

# Inset params
resolver.resolve("$AUTO_INSET")       # -> 0.06 (3% of 2.0)
resolver.resolve("$AUTO_INSET_THICK") # -> 0.10 (5% of 2.0)

# Extrude params
resolver.resolve("$AUTO_EXTRUDE")     # -> 0.05 (10% of 0.5)
resolver.resolve("$AUTO_EXTRUDE_NEG") # -> -0.05 (inward)

# Scale params (return lists)
resolver.resolve("$AUTO_SCALE_SMALL") # -> [1.6, 3.2, 0.4]
```

---

## Available $AUTO_* Parameters

### Bevel Parameters

| Parameter | Formula | Use Case |
|-----------|---------|----------|
| `$AUTO_BEVEL` | `min(dims) * 0.05` | Standard edge bevel |
| `$AUTO_BEVEL_SMALL` | `min(dims) * 0.02` | Subtle edge bevel |
| `$AUTO_BEVEL_LARGE` | `min(dims) * 0.10` | Prominent edge bevel |

### Inset Parameters

| Parameter | Formula | Use Case |
|-----------|---------|----------|
| `$AUTO_INSET` | `min(x, y) * 0.03` | Standard face inset |
| `$AUTO_INSET_THICK` | `min(x, y) * 0.05` | Thicker face inset |

### Extrude Parameters

| Parameter | Formula | Use Case |
|-----------|---------|----------|
| `$AUTO_EXTRUDE` | `z * 0.10` | Standard outward extrude |
| `$AUTO_EXTRUDE_SMALL` | `z * 0.05` | Subtle extrude |
| `$AUTO_EXTRUDE_DEEP` | `z * 0.20` | Deep extrude |
| `$AUTO_EXTRUDE_NEG` | `-z * 0.10` | Inward extrude |

### Scale Parameters

| Parameter | Formula | Use Case |
|-----------|---------|----------|
| `$AUTO_SCALE_SMALL` | `[x*0.8, y*0.8, z*0.8]` | Shrink to 80% |
| `$AUTO_SCALE_TINY` | `[x*0.5, y*0.5, z*0.5]` | Shrink to 50% |

### Other Parameters

| Parameter | Formula | Use Case |
|-----------|---------|----------|
| `$AUTO_OFFSET` | `min(dims) * 0.02` | Small offset |
| `$AUTO_THICKNESS` | `z * 0.05` | Shell thickness |
| `$AUTO_SCREEN_DEPTH` | `z * 0.50` | Phone screen depth |
| `$AUTO_SCREEN_DEPTH_NEG` | `-z * 0.50` | Inward screen |
| `$AUTO_LOOP_POS` | `0.8` | Loop cut position |

---

## WorkflowRegistry Integration

### Setup in expand_workflow

```python
def expand_workflow(self, workflow_name, params=None, context=None):
    # ... existing setup ...

    # Set up proportion resolver (TASK-041-14)
    self._setup_proportion_resolver(context or {})

    # ... continue with expansion ...

def _setup_proportion_resolver(self, context):
    dimensions = None

    # Try "dimensions" key
    if "dimensions" in context:
        dimensions = context["dimensions"]
    # Try width/height/depth keys
    elif all(k in context for k in ["width", "height", "depth"]):
        dimensions = [context["width"], context["height"], context["depth"]]

    if dimensions and len(dimensions) >= 3:
        self._proportion_resolver.set_dimensions(dimensions)
    else:
        self._proportion_resolver.clear_dimensions()
```

### Resolution in _resolve_single_value

```python
def _resolve_single_value(self, value, params):
    # ... handle lists and dicts ...

    if not isinstance(value, str):
        return value

    # $CALCULATE first
    if value.startswith("$CALCULATE("):
        result = self._evaluator.resolve_param_value(value)
        if result != value:
            return result

    # $AUTO_* second
    if value.startswith("$AUTO_"):
        result = self._proportion_resolver.resolve(value)
        if result != value:
            return result

    # Simple $variable last
    if value.startswith("$") and not value.startswith("$CALCULATE") and not value.startswith("$AUTO_"):
        # ... variable lookup ...
```

---

## Resolution Priority

When a value could match multiple patterns, the order is:

1. **$CALCULATE(...)** - ExpressionEvaluator
2. **$AUTO_*** - ProportionResolver
3. **$variable** - Simple context lookup
4. **Literal** - Pass through unchanged

---

## Fallback Behavior

When dimensions are not available:

```python
resolver = ProportionResolver()
# No dimensions set

result = resolver.resolve("$AUTO_BEVEL")
# -> "$AUTO_BEVEL" (unchanged string)
```

This allows workflows to continue even with incomplete context. The user can then set values manually if needed.

---

## Testing

### Unit Tests (42)

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/evaluator/test_proportion_resolver.py -v
```

Test classes:
- `TestProportionResolverInit` - Initialization and dimensions
- `TestBevelParams` - $AUTO_BEVEL*
- `TestInsetParams` - $AUTO_INSET*
- `TestExtrudeParams` - $AUTO_EXTRUDE*
- `TestScaleParams` - $AUTO_SCALE*
- `TestOtherParams` - Remaining params
- `TestResolvePassthrough` - Non-AUTO values
- `TestResolveRecursive` - Lists and dicts
- `TestResolveParams` - Batch resolution
- `TestNoDimensions` - Fallback behavior
- `TestRealWorldExamples` - Phone, table, tower

### Integration Tests (6)

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/workflows/test_registry_proportions.py -v
```

Test classes:
- `TestRegistryProportionResolver` - Basic integration
- `TestMixedParameters` - $AUTO + $CALCULATE
- `TestAutoScaleParams` - List return values
- `TestRealWorldWorkflows` - Phone workflow

---

## YAML Examples

### Phone Workflow

```yaml
name: phone_auto
steps:
  - tool: mesh_bevel
    params:
      offset: "$AUTO_BEVEL"  # Adapts to phone thickness
      segments: 3

  - tool: mesh_inset
    params:
      thickness: "$AUTO_INSET"  # Adapts to phone width

  - tool: mesh_extrude_region
    params:
      move: [0, 0, "$AUTO_SCREEN_DEPTH_NEG"]  # 50% of thickness inward
```

### Table Workflow

```yaml
name: table_auto
steps:
  - tool: mesh_bevel
    params:
      offset: "$AUTO_BEVEL_LARGE"  # More prominent bevel for furniture

  - tool: mesh_extrude_region
    params:
      move: [0, 0, "$AUTO_EXTRUDE_NEG"]  # Leg extrusion
```

### Mixed Parameters

```yaml
steps:
  - tool: mesh_bevel
    params:
      offset: "$AUTO_BEVEL"  # ProportionResolver
      segments: 3           # Literal

  - tool: mesh_inset
    params:
      thickness: "$CALCULATE(min_dim * 0.03)"  # ExpressionEvaluator

  - tool: mesh_extrude_region
    params:
      move: [0, 0, "$depth"]  # Simple variable

    condition: "has_selection"  # ConditionEvaluator
```

---

## Adding New AUTO Parameters

To add a new parameter:

1. Add calculation method in ProportionResolver:
```python
def _calc_new_param(self) -> float:
    """Calculate new param (description)."""
    return self._dimensions[2] * 0.15  # Example
```

2. Add to AUTO_PARAMS dict:
```python
"$AUTO_NEW_PARAM": {
    "calculation": self._calc_new_param,
    "description": "15% of Z height",
    "returns": "float",  # or "list"
},
```

3. Add tests in test_proportion_resolver.py
