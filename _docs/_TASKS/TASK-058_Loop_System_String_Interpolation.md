# TASK-058: Loop System & String Interpolation for Workflows

## Overview

Extension of the workflow system with **loops** and **string interpolation** so that even complex workflows (furniture/devices/models) can be described briefly and parametrically (e.g. `simple_table.yaml` without 15 manually duplicated planks).

Key assumption: **nothing can "bypass the pipeline"** (especially the adaptation from TASK-051). Loops/interpolation must work identically in the standard and adaptive paths.

---

## DSL Assumptions (TASK-058)

### 1) String interpolation: `{var}` (MUST)

- Placeholders `{var}` are substituted in **every workflow string**: `params`, `description`, `condition`, `id`, `depends_on` (+ optionally in dynamic attrs).
- Interpolation is executed **before** `$CALCULATE/$AUTO_/$variable` and before `condition` evaluation, so `{i}` can appear inside `$CALCULATE(...)` and `condition`.
- Interpolation is common for loops and “normal” steps (this is not just a loop feature).
- Escaping: `{{` and `}}` denote literal `{` and `}` (no interpolation).
- No `$FORMAT(...)` in the core DSL. One syntax `{var}` simplifies authoring and automatically supports nested loops.

### 2) Loops: `loop` (MUST)

A loop is configured at the step level (`WorkflowStep.loop`) and expanded by `LoopExpander`.

Supported variants:

**A. Single variable:**
```yaml
loop:
  variable: i
  range: "1..plank_count"   # inclusive
```

**B. Nested loops (multiple variables, cross‑product):**
```yaml
loop:
  variables: [row, col]
  ranges: ["0..3", "0..4"]
```

**C. Iteration over values (optional, but very useful):**
```yaml
loop:
  variable: side
  values: ["L", "R"]
```

### 3) Execution order in a loop: `loop.group` (MUST)

By default the loop expands “step by step” (first the whole loop for step A, then the whole loop for step B).

To obtain correct per‑iteration ordering (e.g. `create_i → transform_i → edit_i`), steps may share:
```yaml
loop:
  group: planks
  variable: i
  range: "1..plank_count"
```

`LoopExpander` interleaves (zips) the expansion of *consecutive, adjacent* steps that have the same `loop.group` and the same iteration space.

### 4) Safeguards (MUST)

- `LoopExpander` has a limit on the maximum number of generated steps (protection against accidentally `1..100000`).
- Interpolation is strict: if a string contains `{var}` and `var` does not exist in the context → error (to avoid “fail‑open” in `condition`).

## Current Architecture

### Workflow Processing Pipeline

```
YAML File
    ↓
WorkflowLoader._parse_step()          # Parses YAML → WorkflowStep
    ↓
WorkflowRegistry.expand_workflow()    # Main expansion method
    ├── _build_variables()            # defaults + modifiers
    ├── resolve_computed_parameters() # TASK-056-5 (computed params)
    ├── LoopExpander.expand()         # TASK-058 (loop expansion + {var} interpolation)
    ├── _resolve_definition_params()  # $variable, $CALCULATE substitution
    └── _steps_to_calls()             # Condition validation, → CorrectedToolCall[]
```

### ⚠️ Critical: Adaptation (TASK-051) currently bypasses the pipeline

When workflow adaptation is enabled (`TASK-051`) the router has a separate path that **does not** use `WorkflowRegistry.expand_workflow()` and therefore bypasses key pipeline elements.

**Current behavior (BUG):** `server/router/application/router.py:_expand_triggered_workflow()` in the branch `should_adapt == True`:
- does not run computed params (`resolve_computed_parameters()` in registry),
- does not resolve `$CALCULATE(...)` and `$AUTO_*`,
- does not run `condition` + `simulate_step_effect()` (so conditional steps stop working),
- thus it will also bypass the loop system from TASK-058.

**TASK-058 requirement:** adaptation must only be a filter of steps (core vs optional), and the **rest** of expansion must go through the same path as standard expansion in the registry.

### Key Files (Clean Architecture)

| Layer | File | Role |
|---------|------|------|
| **Application/Workflows** | `server/router/application/workflows/base.py:17-136` | `WorkflowStep` dataclass (fields: tool, params, condition, loop?) |
| **Infrastructure** | `server/router/infrastructure/workflow_loader.py:300` | `_parse_step()` - parsing YAML → WorkflowStep |
| **Application/Evaluator** | `server/router/application/evaluator/expression_evaluator.py:57-60` | `$CALCULATE` patterns + `$variable` |
| **Application/Evaluator** | `server/router/application/evaluator/unified_evaluator.py:45` | Whitelist of functions + AST core (TASK-060) |
| **Application/Workflows** | `server/router/application/workflows/registry.py:202` | `expand_workflow()` - main expansion |
| **Application/Workflows** | `server/router/application/workflows/registry.py:541` | `_resolve_definition_params()` / `$CALCULATE` + `$variable` |
| **Application/Router** | `server/router/application/router.py:433` | `_expand_triggered_workflow()` - adaptation path (TASK-051) |
| **Application/Engines** | `server/router/application/engines/workflow_adapter.py` | `WorkflowAdapter` - filtering optional steps |

---

## Implementation Proposal

## Definition of Done (Acceptance)

- [ ] Adaptation (TASK-051) does not bypass the pipeline: computed params, `$CALCULATE`, `$AUTO_*`, `condition` + `simulate_step_effect()` and loops/interpolation work identically as without adaptation.
- [ ] `WorkflowRegistry.expand_workflow()` accepts `steps_override` and uses it as the source of steps (shared path for adaptation).
- [ ] `loop` in YAML is parsed automatically by `WorkflowLoader` (no changes in the loader).
- [ ] `LoopExpander` supports: `range` (inclusive), `values`, nested loops (`variables`+`ranges`) and `loop.group` (interleaving).
- [ ] String interpolation `{var}` works in: `params`, `description`, `condition`, `id`, `depends_on` (+ dynamic attrs if they are of type str/list/dict).
- [ ] Interpolation is executed before `$CALCULATE/$AUTO_/$variable` and before `condition` evaluation.
- [ ] Loop expansion removes `loop` in the resulting steps (expanded steps are “concrete”).
- [ ] `_resolve_definition_params()` preserves all `WorkflowStep` fields and dynamic attributes (does not lose: `optional/tags/disable_adaptation/id/depends_on/...`).
- [ ] Limit on the maximum number of generated steps + error for unknown `{var}` placeholders.
- [ ] Tests: adaptation regression + unit tests for loops/interpolation (+ interleaving test).

### PHASE 0: Fix workflow adaptation (P0 - MUST)

**Goal:** Regardless of whether adaptation is enabled, the workflow should go through the **same** expansion pipeline as standard (`WorkflowRegistry.expand_workflow()`), so as not to break:
- `condition` + context simulation,
- `$CALCULATE(...)` / `$AUTO_*`,
- computed params,
- loops (TASK-058).

#### 0.1 Principle

1. Router selects `adapted_steps` (this is the only adaptation logic).
2. Then it delegates the “everything else” (computed params, loop expansion, param resolution, condition evaluation) to `WorkflowRegistry`.

#### 0.2 Minimal change in registry API (recommended)

Add an optional parameter to `WorkflowRegistry.expand_workflow()`:

```python
def expand_workflow(
    self,
    workflow_name: str,
    params: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    user_prompt: Optional[str] = None,
    steps_override: Optional[List[WorkflowStep]] = None,  # TASK-058/TASK-051: NEW
) -> List[CorrectedToolCall]:
    ...
```

In the “custom definition” branch use:
```python
steps_source = steps_override if steps_override is not None else definition.steps
```

#### 0.3 Change in router (TASK-051)

In the branch `should_adapt == True` in `server/router/application/router.py:_expand_triggered_workflow()` remove the manual construction of `CorrectedToolCall` and replace it with:

```python
calls = registry.expand_workflow(
    workflow_name,
    merged_params,
    eval_context,
    user_prompt=self._current_goal or "",
    steps_override=adapted_steps,  # <<<< key
)
```

**Acceptance:** workflow with adaptation has identical support for `$CALCULATE/$AUTO_/computed/condition` as without adaptation (it only differs by the list of steps).

### PHASE 1: Loops + String Interpolation (P0 - Critical)

#### 1.1 New `loop` Parameter in WorkflowStep

**File**: `server/router/application/workflows/base.py:17-95`

Add a new field to the `WorkflowStep` dataclass (after line 58, before `def __post_init__`):

```python
@dataclass
class WorkflowStep:
    # ... existing fields (tool, params, description, condition, optional, etc.) ...

    # TASK-058: Loop parameter for step repetition
    loop: Optional[Dict[str, Any]] = None
```

**IMPORTANT**: Add `"loop"` to `_known_fields` in `__post_init__()` (lines 69-74 in the current code):
```python
self._known_fields = {
    "tool", "params", "description", "condition",
    "optional", "disable_adaptation", "tags",
    "id", "depends_on", "timeout", "max_retries",
    "retry_delay", "on_failure", "priority",
    "loop"  # TASK-058: NEW
}
```

**Loop Schema**:
```yaml
loop:
  # A) Single variable range (inclusive)
  variable: i
  range: "1..plank_count"          # start/end can be numbers, names, or expressions
  # range: [1, 15]                 # alternatively: static [start, end]

  # (optional) C) Iterate over a list of values (instead of range)
  # values: ["L", "R"]

  # (optional) Interleaving of consecutive steps that share the same loop
  # group: "planks"

  # B) Nested loops (instead of variable/range):
  # variables: [row, col]
  # ranges: ["0..(rows - 1)", "0..(cols - 1)"]
```

**Using loop variables in params/conditions (MUST):**

- LoopExpander performs **placeholder substitution** in strings: `{i}` → `3` (similarly `{row}`, `{col}`, `{side}`, etc.).
- To use a loop variable in `$CALCULATE(...)` or `condition`, always use **`{var}`**, not bare `var`.

Examples:
```yaml
params:
  name: "TablePlank_{i}"  # recommended (without $FORMAT)
  location:
    - "$CALCULATE(-table_width/2 + plank_actual_width * ({i} - 0.5))"
    - 0
    - "$CALCULATE(leg_length + 0.0114)"

condition: "{i} <= plank_count"
description: "Create plank {i}"
```

This is critical, because without additional logic “injecting i into the evaluator context” an expression with bare `i` will not work.

#### 1.2 LoopExpander - NEW FILE (Application Layer)

**File**: `server/router/application/evaluator/loop_expander.py` (NEW FILE)

> **Clean Architecture**: `LoopExpander` is application logic (data transformation),
> so it belongs to the `application/evaluator/` layer alongside `expression_evaluator.py`.

```python
"""
LoopExpander (TASK-058).

Responsible for:
- loop expansion (range/values, single + nested)
- string interpolation `{var}` (strict, with escaping {{ }})
- interleaving steps with the same loop.group
- preserving WorkflowStep fields + dynamic attrs
"""

import dataclasses
import itertools
import logging
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator
from server.router.application.workflows.base import WorkflowStep

logger = logging.getLogger(__name__)


class LoopExpander:
    def __init__(self, max_expanded_steps: int = 2000):
        self._max_expanded_steps = max_expanded_steps
        self._evaluator = UnifiedEvaluator()

    def expand(self, steps: List[WorkflowStep], context: Dict[str, Any]) -> List[WorkflowStep]:
        """Expand loops + interpolate `{var}`.

        - Steps without loop: only interpolation.
        - Steps with loop without group: expansion “step by step”.
        - Steps with the same loop.group (consecutive, adjacent): interleaving per iteration.
        """
        expanded: List[WorkflowStep] = []
        i = 0
        while i < len(steps):
            step = steps[i]
            loop_cfg = step.loop or {}

            group = loop_cfg.get("group")
            if group:
                block = self._consume_group_block(steps, i)
                expanded.extend(self._expand_group_block(block, context))
                i += len(block)
                continue

            expanded.extend(self._expand_step(step, context))
            i += 1

        if len(expanded) > self._max_expanded_steps:
            raise ValueError(
                f"Loop expansion produced {len(expanded)} steps "
                f"(limit={self._max_expanded_steps})."
            )
        return expanded

    def _expand_group_block(self, steps: Sequence[WorkflowStep], ctx: Dict[str, Any]) -> List[WorkflowStep]:
        # 1) verify that all steps have compatible loop “iteration space”
        # 2) generate all iterations (iter contexts)
        # 3) for each iteration: emit steps in the YAML order (zip/interleave)
        ...

    def _expand_step(self, step: WorkflowStep, ctx: Dict[str, Any]) -> List[WorkflowStep]:
        if not step.loop:
            return [self._interpolate_step(step, ctx)]

        out: List[WorkflowStep] = []
        for iter_ctx in self._iter_loop_contexts(step.loop, ctx):
            concrete = self._clone_step(step, loop=None)
            out.append(self._interpolate_step(concrete, iter_ctx))
        return out

    def _iter_loop_contexts(self, loop_cfg: Dict[str, Any], ctx: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        # Single variable + range
        if "variable" in loop_cfg and "range" in loop_cfg:
            var = loop_cfg["variable"]
            for v in self._resolve_range(loop_cfg["range"], ctx):
                yield {**ctx, var: v}
            return

        # Single variable + values
        if "variable" in loop_cfg and "values" in loop_cfg:
            var = loop_cfg["variable"]
            for v in loop_cfg["values"]:
                yield {**ctx, var: v}
            return

        # Nested loops
        if "variables" in loop_cfg and "ranges" in loop_cfg:
            vars_ = list(loop_cfg["variables"])
            ranges = [list(self._resolve_range(r, ctx)) for r in loop_cfg["ranges"]]
            for combo in itertools.product(*ranges):
                yield {**ctx, **dict(zip(vars_, combo))}
            return

        raise ValueError(f"Invalid loop config: {loop_cfg}")

    def _resolve_range(self, range_spec: Any, ctx: Dict[str, Any]) -> range:
        # [start, end]
        if isinstance(range_spec, (list, tuple)) and len(range_spec) == 2:
            start, end = range_spec
            return range(int(start), int(end) + 1)

        # "start..end" (inclusive) — start/end can be expressions
        if isinstance(range_spec, str) and ".." in range_spec:
            start_expr, end_expr = [p.strip() for p in range_spec.split("..", 1)]
            start = self._eval_int(start_expr, ctx)
            end = self._eval_int(end_expr, ctx)
            return range(start, end + 1)

        raise ValueError(f"Invalid range spec: {range_spec}")

    def _eval_int(self, expr: str, ctx: Dict[str, Any]) -> int:
        self._evaluator.set_context(ctx)
        return int(self._evaluator.evaluate_as_float(expr))

    def _interpolate_step(self, step: WorkflowStep, ctx: Dict[str, Any]) -> WorkflowStep:
        # Interpolates: params/description/condition/id/depends_on + (optionally) dynamic attrs.
        ...

    def _clone_step(self, step: WorkflowStep, **overrides: Any) -> WorkflowStep:
        # Clones all dataclass fields + carries dynamic attrs.
        data = dataclasses.asdict(step)
        data.update(overrides)
        cloned = WorkflowStep(**{k: v for k, v in data.items() if k != "_known_fields"})

        # TODO: copy dynamic attrs (TASK-055-FIX-6 Phase 2)
        return cloned
```

#### 1.3 String interpolation: `{var}` (P0)

In TASK-058 we **do not** add `$FORMAT(...)` — we keep a single `{var}` syntax.

Implementation: interpolation is part of `LoopExpander.expand()` (works for steps in a loop and outside a loop).

Requirements:
- supports escaping `{{`/`}}`,
- works recursively in `params` (list/dict),
- works in `description`, `condition`, `id`, `depends_on`,
- is strict: unknown `{var}` → `ValueError`.

#### 1.4 Integration in WorkflowRegistry

**File**: `server/router/application/workflows/registry.py:34-41`

**Step 1**: Add import at the top of the file (after line 22, alongside other imports from evaluator):

```python
from server.router.application.evaluator.loop_expander import LoopExpander
```

**Step 2**: Add `_loop_expander` in `__init__()` (lines 34-41 in the current code, after line 41):

```python
def __init__(self):
    """Initialize registry with workflows from YAML/JSON files."""
    self._workflows: Dict[str, BaseWorkflow] = {}
    self._custom_definitions: Dict[str, WorkflowDefinition] = {}
    self._custom_loaded: bool = False
    self._evaluator = ExpressionEvaluator()
    self._condition_evaluator = ConditionEvaluator()
    self._proportion_resolver = ProportionResolver()
    self._loop_expander = LoopExpander()  # TASK-058: NEW
```

**Step 3**: In `expand_workflow()` (lines 289-295 in the current code) add loop expansion BEFORE `_resolve_definition_params()`:

```python
# Try custom definition
definition = self._custom_definitions.get(workflow_name)
if definition:
    steps_source = steps_override if steps_override is not None else definition.steps

    # Build variable context from defaults + modifiers (TASK-052)
    variables = self._build_variables(definition, user_prompt)
    # Merge with params (params override variables)
    all_params = {**variables, **(params or {})}

    # TASK-055-FIX-7 Phase 0: Resolve computed parameters
    if definition.parameters:
        # ... existing computed params code ...

    # Set evaluator context with all resolved parameters
    self._evaluator.set_context({**base_context, **all_params})

    # TASK-058: Loop expansion + {var} interpolation BEFORE other processing
    expanded_steps = self._loop_expander.expand(
        steps_source,
        {**base_context, **all_params}  # Includes plank_count + any other context
    )

    steps = self._resolve_definition_params(expanded_steps, all_params)
    return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

#### 1.5 Integration of loops + param resolution with adaptation (TASK-051)

After implementing **PHASE 0** (steps_override), the loop system will work automatically in adaptation as well:
- adaptation selects `adapted_steps`,
- registry does: computed params → loop expansion → param resolution → `condition` + simulation.

This closes the “split brain” between the standard and adaptive paths.

---

### ✅ Conditional Expressions in `$CALCULATE(...)` (Done in TASK-060)

> **Implemented**: Comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`), logical operators (`and`, `or`, `not`) and ternary expressions (`x if cond else y`) are available after **TASK-060: Unified Expression Evaluator**.
>
> **Historical note**: previously this was separated into TASK-059, but TASK-059 is marked as superseded by TASK-060 and remains only as a reference:
> [TASK-059: Expression Evaluator - Logical & Comparison Operators](./TASK-059_Expression_Evaluator_Logical_Operators.md)

---

### Nested Loops (P0 - part of PHASE 1)

Nested loops are part of the core functionality (not “future”), because they significantly shorten workflows for grids (e.g. windows in a facade, phone keys, shelf modules).

Example (3x4 grid):
```yaml
- tool: modeling_create_primitive
  params:
    name: "Button_{row}_{col}"
  loop:
    variables: [row, col]
    ranges: ["0..(rows - 1)", "0..(cols - 1)"]
    group: buttons
  description: "Create button r={row}, c={col}"
```

---

## Example After Implementation

### simple_table.yaml (BEFORE - 200+ lines)

```yaml
steps:
  # Plank 1
  - tool: modeling_create_primitive
    params:
      name: "TablePlank_1"
  - tool: modeling_transform_object
    params:
      name: "TablePlank_1"
      location: ["$CALCULATE(-table_width/2 + plank_actual_width * 0.5)", ...]

  # Plank 2 (condition: plank_count >= 2)
  - tool: modeling_create_primitive
    params:
      name: "TablePlank_2"
    condition: "plank_count >= 2"
  # ... repeat for 15 planks ...
```

### simple_table.yaml (AFTER - ~30 lines)

```yaml
steps:
  # All planks via loop
  - tool: modeling_create_primitive
    params:
      name: "TablePlank_{i}"  # Recommended (LoopExpander will substitute {i})
    loop:
      variable: "i"
      range: "1..plank_count"
      group: "planks"
    description: "Create table plank {i}"

  - tool: modeling_transform_object
    params:
      name: "TablePlank_{i}"
      scale: ["$CALCULATE(plank_actual_width / 2)", "$CALCULATE(table_length / 2)", 0.0114]
      location: ["$CALCULATE(-table_width/2 + plank_actual_width * ({i} - 0.5))", 0, "$CALCULATE(leg_length + 0.0114)"]
    loop:
      variable: "i"
      range: "1..plank_count"
      group: "planks"
    description: "Position plank {i}"
```

> **Tip (readability):** repeated `loop:` can be easily shortened with YAML anchors (`&`/`*`) and `<<` merge (PyYAML `safe_load` supports this).

---

## Files To Modify (Clean Architecture)

### Phase 0 (Adaptation does not bypass pipeline - TASK-051)

| Layer | File | Change | Priority |
|---------|------|--------|-----------|
| **Application/Workflows** | `server/router/application/workflows/registry.py` | Add `steps_override` to `expand_workflow()` and use it as the source of steps for custom workflows | P0 |
| **Application/Router** | `server/router/application/router.py` | In adaptation call `registry.expand_workflow(..., steps_override=adapted_steps)` instead of manually building tool calls | P0 |

### Phase 1 (Loop + String Interpolation)

| Layer | File | Change | Priority |
|---------|------|--------|-----------|
| **Application/Workflows** | `server/router/application/workflows/base.py` | Add `loop: Optional[Dict]` to `WorkflowStep`, add `"loop"` to `_known_fields`, include `loop` in `to_dict()` | P0 |
| **Infrastructure** | `server/router/infrastructure/workflow_loader.py` | Automatic handling of `loop` by existing `_parse_step()` (no changes) | P0 |
| **Application/Evaluator** | `server/router/application/evaluator/loop_expander.py` | **NEW FILE**: `LoopExpander` class | P0 |
| **Application/Evaluator** | `server/router/application/evaluator/__init__.py` | Add export of `LoopExpander` to `__all__` | P0 |
| **Application/Workflows** | `server/router/application/workflows/registry.py` | Import `LoopExpander`, add `_loop_expander`, integrate loop expansion in `expand_workflow()` (for custom + `steps_override`) | P0 |
| **Application/Workflows** | `server/router/application/workflows/registry.py` | Fix `_resolve_definition_params()` so it does not lose step fields (optional/tags/depends_on/loop/dynamic attrs) | P0 |
| **Custom Workflows** | `server/router/application/workflows/custom/simple_table.yaml` | Rewrite to loop syntax (optional in Phase 1) | P0 |
| **Docs** | `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md` | Add Loops + `{var}` interpolation section | P0 |
| **Docs** | `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md` | Add Loops + refactor example section | P0 |
| **Docs** | `_docs/_ROUTER/WORKFLOWS/expression-reference.md` | Add `{var}` interpolation + pipeline ordering | P0 |

### ✅ Conditional Expressions (already available)

> Comparison/logic/ternary in `$CALCULATE(...)` is available after TASK-060. No implementation required within TASK-058.

---

## Tests (Clean Architecture)

### Unit Tests

```
tests/unit/router/application/workflows/test_workflow_adaptation_pipeline.py
- test_adaptation_uses_registry_pipeline_resolves_calculate_and_auto
- test_adaptation_respects_condition_and_simulation
- test_adaptation_supports_steps_override

tests/unit/router/application/evaluator/test_loop_expander.py
- test_expand_static_range
- test_expand_dynamic_range_expressions
- test_expand_values_list
- test_expand_nested_loops_cross_product
- test_interleaves_grouped_loops
- test_substitutes_placeholders_in_params_condition_description_id_depends_on
- test_substitutes_placeholders_inside_calculate_expression
- test_no_loop_passthrough
- test_invalid_loop_config_raises_error
```

### E2E Tests

```
tests/e2e/router/test_simple_table_with_loops.py
- test_table_with_8_planks_via_loop
- test_table_width_0_73m_fractional_planks
- test_loop_expansion_in_registry
```

---

## Implementation Order (Clean Architecture)

### Phase 0 - Fix adaptation (P0)

| Step | Layer | File | Description |
|------|---------|------|------|
| 0.1 | Application/Workflows | `registry.py` | Add `steps_override` to `expand_workflow()` and use as source of steps |
| 0.2 | Application/Router | `router.py` | Adaptation should delegate to `registry.expand_workflow(..., steps_override=adapted_steps)` |
| 0.3 | Tests | `test_workflow_adaptation_pipeline.py` | Regression tests for: `$CALCULATE/$AUTO_`, `condition`, context simulation |

### Phase 1 - Core Loop System (P0)

| Step | Layer | File | Description |
|------|---------|------|------|
| 1 | Application/Workflows | `base.py` | Add `loop: Optional[Dict]` to `WorkflowStep` + `_known_fields` + `to_dict()` |
| 2 | Infrastructure | `workflow_loader.py` | Verification - `loop` field parsed automatically (no changes) |
| 3 | Application/Evaluator | `loop_expander.py` | **NEW FILE** - `LoopExpander` class |
| 4 | Application/Evaluator | `__init__.py` | Add import and export of `LoopExpander` to `__all__` |
| 5 | Application/Workflows | `registry.py` | Integration: loop expansion + `{var}` interpolation before `_resolve_definition_params()` (also for `steps_override`) |
| 6 | Application/Workflows | `registry.py` | Fix `_resolve_definition_params()` (do not lose fields/dynamic attrs) |
| 7 | Tests | `test_loop_expander.py` | Unit tests: range/values/nested/group + `{var}` interpolation |
| 8 | Custom Workflows | `simple_table.yaml` | Refactor to loop syntax (optional) |
| 9 | Docs | `_docs/_ROUTER/WORKFLOWS/*.md` | Add Loops + `{var}` interpolation to guides |

### ✅ Phase 2 - Conditional Expressions (closed by TASK-060)

> No work in TASK-058 (done in TASK-060).

---

## Architectural Decisions

1. **Single interpolation**: `{var}` for all strings (no `$FORMAT`).
2. **Loops in core**: single + nested loops and `values`.
3. **Per‑iteration ordering**: `loop.group` enables interleaving without new “block nodes”.
4. **LoopExpander location**: `application/evaluator/` (data transformation, no I/O).
5. **Strict interpolation + limits**: prevents silent errors and explosion of step counts.

Processing order in the pipeline (custom workflows):
1. computed params (TASK-056-5)
2. `LoopExpander.expand()` (loop expansion + `{var}` interpolation)
3. `_resolve_definition_params()` (`$CALCULATE`, `$AUTO_*`, `$variable`)
4. `_steps_to_calls()` (`condition` + `simulate_step_effect()`)

---

## Known Technical Debt

### `_resolve_definition_params()` in registry.py (lines 539-579)

The existing method **does not pass all** `WorkflowStep` fields when creating resolved steps:

```python
# CURRENT IMPLEMENTATION (registry.py:570-577):
resolved_steps.append(
    WorkflowStep(
        tool=step.tool,
        params=resolved_params,
        description=step.description,
        condition=step.condition,  # Only these 4 fields!
    )
)
```

**Missing fields**: `optional`, `disable_adaptation`, `tags`, `id`, `depends_on`, `timeout`, `max_retries`, `retry_delay`, `on_failure`, `priority`

**Recommendation**: During TASK-058 fix this debt by introducing a shared helper for cloning a step (e.g. `_clone_step(step, **overrides)`), which copies all dataclass fields + dynamic attrs; use it in `LoopExpander` and in `_resolve_definition_params()`.

---

## Estimated Implementation Time

| Step | Time |
|------|------|
| PHASE 0: Adaptation uses registry pipeline | 10-20 min |
| `WorkflowStep.loop` + `_known_fields` | 5 min |
| Loop parsing verification | 0 min (automatic) |
| `LoopExpander` class (nested + group + strict interpolation) | 45-60 min |
| `__init__.py` update | 2 min |
| Registry integration | 10 min |
| Fix `_resolve_definition_params()` (technical debt) | 5 min |
| Unit tests (`LoopExpander`) | 20 min |
| `simple_table.yaml` refactor (optional) | 15 min |
| Docs update (_docs/_ROUTER/WORKFLOWS/*) | 20-30 min |
| **TOTAL TASK-058** | **~2-3h** |

> **Note**: Conditional expressions (ternary, comparisons, logical operators) are already available after **TASK-060**, so they do not increase TASK-058 scope.

---

## Codebase Compatibility Check (2025-12-12)

### ✅ Verified File Locations

| Element | Path in TASK-058 | Status |
|---------|-------------------|--------|
| `WorkflowStep` | `server/router/application/workflows/base.py` | ✅ Correct |
| `ExpressionEvaluator` | `server/router/application/evaluator/expression_evaluator.py` | ✅ Correct |
| `WorkflowRegistry` | `server/router/application/workflows/registry.py` | ✅ Correct |
| `Router` (adaptation) | `server/router/application/router.py` | ✅ Needs fix (PHASE 0) |
| `workflow_loader` | `server/router/infrastructure/workflow_loader.py` | ✅ Correct |
| `evaluator/__init__.py` | `server/router/application/evaluator/__init__.py` | ✅ Correct |

### ✅ Verified Line Numbers

| Element | Lines in TASK-058 | Current lines | Status |
|---------|-----------------|----------------|--------|
| `WorkflowStep` dataclass | 17-95 | 17-136 | ✅ OK (extended) |
| `_known_fields` | 69-74 | 69-74 | ✅ Exact |
| `CALCULATE_PATTERN` | 83-87 | 57 | ✅ OK |
| `VARIABLE_PATTERN` | 87 | 60 | ✅ OK |
| `resolve_param_value()` | 168-205 | 158-191 | ✅ OK |
| `_eval_node()` | 262-336 | `unified_evaluator.py:231` | ✅ Moved in TASK-060 |
| `expand_workflow()` | 202-297 | 202-297 | ✅ Exact |
| `_resolve_definition_params()` | 539-632 | 541 | ✅ OK |
| `_parse_step()` | 300-350 | 300-350 | ✅ OK |
| `_expand_triggered_workflow()` (adaptation) | - | `router.py:433-543` | ⚠️ Requires PHASE 0 |

### ✅ Compliance with Clean Architecture

| Aspect | Assessment |
|--------|-------|
| `LoopExpander` in `application/evaluator/` | ✅ Correct layer (application logic) |
| Dependency direction | ✅ Inner → Outer |
| Separation of concerns | ✅ Data transformation separated from I/O |

### 📝 Illustration of Changes

#### Change 0: Adaptation does not bypass registry pipeline (PHASE 0)

BEFORE (`router.py:_expand_triggered_workflow()`):
- manual construction of `CorrectedToolCall`,
- missing `$CALCULATE/$AUTO_`, missing `condition`, missing `simulate_step_effect()`.

AFTER (PHASE 0):
```python
calls = registry.expand_workflow(
    workflow_name,
    merged_params,
    eval_context,
    user_prompt=self._current_goal or "",
    steps_override=adapted_steps,
)
```

#### Change 1: `_known_fields` in WorkflowStep

BEFORE (`base.py:69-74`):
```python
self._known_fields = {
    "tool", "params", "description", "condition",
    "optional", "disable_adaptation", "tags",
    "id", "depends_on", "timeout", "max_retries",
    "retry_delay", "on_failure", "priority"
}
```

AFTER (TASK-058):
```python
self._known_fields = {
    "tool", "params", "description", "condition",
    "optional", "disable_adaptation", "tags",
    "id", "depends_on", "timeout", "max_retries",
    "retry_delay", "on_failure", "priority",
    "loop"  # TASK-058: NEW
}
```

#### Change 2: Integration in `expand_workflow()`

BEFORE (`registry.py:289-295`):
```python
# Set evaluator context with all resolved parameters
self._evaluator.set_context({**base_context, **all_params})

steps = self._resolve_definition_params(definition.steps, all_params)
return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

AFTER (TASK-058):
```python
# Set evaluator context with all resolved parameters
self._evaluator.set_context({**base_context, **all_params})

steps_source = steps_override if steps_override is not None else definition.steps

# TASK-058: Loop expansion + {var} interpolation BEFORE other processing
expanded_steps = self._loop_expander.expand(
    steps_source,
    {**base_context, **all_params}
)

steps = self._resolve_definition_params(expanded_steps, all_params)
return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

### ✅ Confirmation of Automatic `loop` Handling in WorkflowLoader

The `_parse_step()` method (`workflow_loader.py:323-340`) uses dynamic loading of fields:

```python
step_fields = {f.name: f for f in dataclasses.fields(WorkflowStep)}
step_data = {}
for field_name, field_info in step_fields.items():
    if field_name in data:
        step_data[field_name] = data[field_name]
    # ... defaults handling
```

After adding `loop: Optional[Dict[str, Any]] = None` to the `WorkflowStep` dataclass, the `loop` field will be **automatically parsed** from YAML without changes in `workflow_loader.py`.

### 🎯 Verification Summary

| Category | Status |
|-----------|--------|
| File paths | ✅ 100% compliant |
| Line numbers | ✅ Updated after TASK-060 |
| Clean Architecture | ✅ Followed |
| Technical debt | ✅ Properly identified |
| Implementation order | ✅ Sensible |

**TASK-058 is compatible with the current code after TASK-060 and can be implemented without architectural changes.**

---

## Related Tasks

| Task | Relation | Description |
|------|---------|------|
| **TASK-060** | **Enables** | Comparisons/logic/ternary in `$CALCULATE` + math in `condition` (already implemented) |
| TASK-059 | Superseded | Left as reference (replaced by TASK-060) |
| TASK-056-1 | Prerequisite | Extended Expression Evaluator (22 math functions) |
| TASK-056-5 | Prerequisite | Computed Parameters |
| TASK-055-FIX-8 | Documentation | Documentation of expression evaluator functions |

> **Implementation order**: TASK-060 (✅) → TASK-058 (Loop System) → full dynamic workflow functionality
