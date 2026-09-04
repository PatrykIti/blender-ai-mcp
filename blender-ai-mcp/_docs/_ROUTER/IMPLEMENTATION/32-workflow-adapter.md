# 32. Workflow Adapter (Confidence-Based Step Selection)

> **Task:** TASK-051 | **Status:** ✅ Done (with TASK-058 pipeline alignment)  
> **Layer:** Application (`server/router/application/engines/`)

---

## Overview

`WorkflowAdapter` selects an appropriate subset of workflow steps when the router is not fully confident about the workflow match.

It is intentionally an **early step-selection filter**:

- It does **not** evaluate `condition`.
- It does **not** run `$CALCULATE`, `$AUTO_*`, computed params, or loops.

After TASK-058, adaptation no longer bypasses the registry pipeline: the adapter only returns `adapted_steps`, and the registry handles the full expansion pipeline.

---

## File Location

`server/router/application/engines/workflow_adapter.py`

---

## Core Concepts

### Core vs Optional Steps

- **Core step**: `optional: false` OR `disable_adaptation: true`
- **Optional step**: `optional: true` AND `disable_adaptation: false`

`disable_adaptation: true` forces the step to be treated as core (never removed by adaptation).

### Confidence Levels

The adapter operates on discrete confidence levels (`HIGH`, `MEDIUM`, `LOW`, `NONE`) produced by matchers / ensemble matching.

Strategy:

- `HIGH` → **FULL** (no filtering)
- `MEDIUM` → **FILTERED** (core + relevant optional)
- `LOW` / `NONE` → **CORE_ONLY** (core only)

---

## Relevance Filtering (MEDIUM)

For `MEDIUM`, optional steps are included if they match the prompt via a 3-tier strategy:

1. **Tag match** (`step.tags` keyword hit in prompt)
2. **Semantic filter parameters** (custom boolean attrs like `add_bench: true`)
3. **Semantic similarity** fallback (if a classifier is available)

This keeps workflows compact while still allowing prompt-driven extras.

---

## Integration with Workflow Expansion (TASK-058 Fix)

### Before (buggy behavior)

Adaptation used to build tool calls manually, which bypassed:

- computed params
- `$CALCULATE` / `$AUTO_*`
- `condition` evaluation + context simulation
- loops + `{var}` interpolation

### After (correct behavior)

In `SupervisorRouter._expand_triggered_workflow()`:

1. `WorkflowAdapter.adapt()` returns `adapted_steps`
2. Router delegates to the canonical registry pipeline:

`registry.expand_workflow(..., steps_override=adapted_steps)`

So the only difference between adapted and non-adapted execution is the step list; the pipeline stays identical.

---

## Authoring Guidance

### Prompt-driven optional features → use `optional: true` + tags

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE, name: "BenchLeft" }
  description: "Create bench"
  optional: true
  tags: ["bench", "seating"]
```

### Parameter-driven branching → prefer `condition` and bypass adaptation if needed

If the decision is deterministic (math/params), avoid semantic filtering:

```yaml
- tool: mesh_transform_selected
  params:
    translate: ["$CALCULATE(0.1 if leg_style == 'x' else 0)", 0, 0]
  description: "Stretch leg top for X-frame"
  optional: true
  disable_adaptation: true
  condition: "leg_style == 'x'"
```

---

## Configuration

`RouterConfig`:

- `enable_workflow_adaptation`
- `adaptation_semantic_threshold`

---

## Tests

- Unit tests: `tests/unit/router/application/test_workflow_adapter.py`
- Integration coverage: `tests/unit/router/application/test_supervisor_router.py`

---

## See Also

- `21-workflow-registry.md` (canonical pipeline + `steps_override`)
- `37-loop-expander.md` (loops + `{var}` interpolation)
- `_docs/_ROUTER/WORKFLOWS/workflow-execution-pipeline.md` (two-filter mental model)
    params: { primitive_type: CUBE, name: "BenchLeft" }
    description: Create left bench
    optional: true
    tags: ["bench", "seating", "left"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchRight" }
    description: Create right bench
    optional: true
    tags: ["bench", "seating", "right"]
```

---

## Tests

Located in `tests/unit/router/application/test_workflow_adapter.py`:

```python
def test_high_confidence_returns_all_steps():
    """HIGH confidence executes all steps."""
    adapter = WorkflowAdapter()
    steps, result = adapter.adapt(definition, "HIGH", "prompt")
    assert len(steps) == len(definition.steps)
    assert result.strategy == "FULL"

def test_low_confidence_skips_optional():
    """LOW confidence skips optional steps."""
    adapter = WorkflowAdapter()
    steps, result = adapter.adapt(definition, "LOW", "prompt")
    assert all(not s.optional for s in steps)
    assert result.strategy == "CORE_ONLY"

def test_medium_confidence_filters_by_tags():
    """MEDIUM confidence includes tag-matching optional steps."""
    adapter = WorkflowAdapter()
    steps, result = adapter.adapt(definition, "MEDIUM", "table with benches")
    # "bench" tag matches "benches" in prompt
    assert any("Bench" in s.params.get("name", "") for s in steps)
    assert result.strategy == "FILTERED"
```

**Test Summary:**
- 20 unit tests
- All passing

---

## Adaptation Strategies

| Confidence | Strategy | Behavior |
|------------|----------|----------|
| **HIGH** (≥0.90) | `FULL` | Execute ALL steps |
| **MEDIUM** (≥0.75) | `FILTERED` | Core + tag-matching optional |
| **LOW** (≥0.60) | `CORE_ONLY` | Core steps only |
| **NONE** (<0.60) | `CORE_ONLY` | Core steps only (fallback) |

---

## Expected Results

```
"create a picnic table"       → HIGH (0.92)  → 49 steps (full workflow)
"simple table with 4 legs"    → LOW (0.68)   → ~33 steps (no benches)
"table with benches"          → MEDIUM (0.78) → ~40 steps (core + bench)
```

---

## See Also

- [TASK-051: Confidence-Based Workflow Adaptation](../../_TASKS/TASK-051_Confidence_Based_Workflow_Adaptation.md)
- [Changelog #97](../../_CHANGELOG/97-2025-12-07-confidence-based-workflow-adaptation.md)
- [29-semantic-workflow-matcher.md](./29-semantic-workflow-matcher.md)
- [WORKFLOWS/README.md](../WORKFLOWS/README.md)
