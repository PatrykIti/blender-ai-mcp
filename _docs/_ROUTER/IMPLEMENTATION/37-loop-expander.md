# 37. Loop Expander (Loops + `{var}` Interpolation)

> **Task:** TASK-058 | **Status:** ✅ Done | **Date:** 2025-12-13  
> **Layer:** Application (`server/router/application/evaluator/`)

---

## Overview

`LoopExpander` is responsible for two workflow DSL features:

1. **Loops** (`step.loop`) – repeat a step over a range / values / nested ranges.
2. **String interpolation** (`{var}`) – replace placeholders in workflow strings using the current workflow context.

It runs inside the normal workflow expansion pipeline, so it works both:

- in the standard workflow path, and
- in the adaptation path (TASK-051), after the fix that makes adaptation use the same pipeline.

---

## File Location

`server/router/application/evaluator/loop_expander.py`

---

## Why This Exists

Without loops, workflows for repetitive structures become huge (e.g. 15 planks, grids of buttons, repeated windows).

With loops + interpolation, you can describe the same workflow parametrically:

```yaml
- tool: modeling_create_primitive
  params:
    name: "Plank_{i}"
  loop:
    variable: i
    range: "1..plank_count"
  description: "Create plank {i}"
```

---

## Pipeline Placement (Order Matters)

For custom YAML workflows, the relevant order is:

1. computed params (`parameters.*.computed`)
2. `LoopExpander.expand()` (loop expansion + `{var}` interpolation)
3. `$CALCULATE(...)` / `$AUTO_*` / `$variable` resolution in params
4. `condition` evaluation + context simulation

This ordering enables patterns like:

```yaml
location: ["$CALCULATE(base_x + step * ({i} - 0.5))", 0, 0]
condition: "{i} <= plank_count"
```

---

## DSL: `loop` Schema

`loop` is defined per step (`WorkflowStep.loop: Optional[Dict[str, Any]]`).

### A) Single Variable + Range (inclusive)

```yaml
loop:
  variable: i
  range: "1..plank_count"
```

- `range` supports expression endpoints via `UnifiedEvaluator`
  (e.g. `"0..(rows - 1)"`).
- Both ends are inclusive.

### B) Single Variable + Values

```yaml
loop:
  variable: side
  values: ["L", "R"]
```

### C) Nested Loops (cross‑product)

```yaml
loop:
  variables: [row, col]
  ranges: ["0..(rows - 1)", "0..(cols - 1)"]
```

Iteration order is the natural product order:
`row=0 col=0..N`, then `row=1 col=0..N`, etc.

---

## Ordering: `loop.group` (Interleaving)

By default, each step expands independently, which can lead to:

`create_1..N`, then `transform_1..N`.

To enforce per‑iteration ordering:

```yaml
- tool: modeling_create_primitive
  params: { name: "Plank_{i}", primitive_type: CUBE }
  loop: { group: planks, variable: i, range: "1..plank_count" }

- tool: modeling_transform_object
  params: { name: "Plank_{i}", location: [0, 0, 0] }
  loop: { group: planks, variable: i, range: "1..plank_count" }
```

`LoopExpander` interleaves consecutive steps that share the same `loop.group`
and have the same iteration space (`variable/range` or `variables/ranges`).

---

## String Interpolation: `{var}` (Strict)

### Where It Applies

Interpolation runs on:

- `params` (recursively in lists/dicts)
- `description`
- `condition`
- `id`, `depends_on`
- dynamic attributes (if they are `str`, `list`, or `dict`)

### Rules

- `{var}` is replaced with `str(context[var])`.
- Escaping:
  - `{{` → literal `{`
  - `}}` → literal `}`
- **Strict mode:** unknown placeholders raise an error (no silent fail‑open).

---

## Safety: Expansion Limit

To prevent accidental explosions like `"1..100000"`, the expander enforces:

- `max_expanded_steps` (default: `2000`)

If the limit is exceeded, expansion fails with a clear error.

---

## Integration Points

### WorkflowStep

`WorkflowStep` gained:

- `loop: Optional[Dict[str, Any]]`

### Registry Integration

`WorkflowRegistry.expand_workflow()` calls:

- computed params
- `LoopExpander.expand(steps_source, context)`
- param resolution
- `condition` evaluation

### Adaptation Path (TASK-051)

Adaptation returns `adapted_steps` (filtered step list).  
After TASK-058, the router delegates to the registry pipeline using:

`expand_workflow(..., steps_override=adapted_steps)`

So loops/interpolation work identically for adapted workflows.

---

## Tests

- Unit tests: `tests/unit/router/application/evaluator/test_loop_expander.py`
- Pipeline regression tests: `tests/unit/router/application/workflows/test_registry.py`

---

## See Also

- `21-workflow-registry.md` (pipeline + steps_override)
- `32-workflow-adapter.md` (adaptation step selection)
- `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md` (authoring guide)
- `_docs/_ROUTER/WORKFLOWS/workflow-execution-pipeline.md` (two-filter mental model)

