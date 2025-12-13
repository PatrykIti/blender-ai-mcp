# Workflow Execution Pipeline (Adaptation, Loops, Conditions)

This document explains how the Router turns a workflow definition into actual tool calls, and how **workflow adaptation** (TASK-051) interacts with **`condition`**, **computed params**, and **loops + `{var}` interpolation** (TASK-058).

If you are authoring workflows, this is the “mental model” you want.

---

## High-Level Order (What Runs When)

For custom YAML workflows, the processing order is:

1. **(Optional) Adaptation step selection** (TASK-051)  
   Filters the workflow *step list* based on confidence level and prompt relevance.
2. **Computed parameters** (TASK-056-5)  
   Resolves `parameters.*.computed` (e.g. `plank_count`, `plank_actual_width`).
3. **Loop expansion + `{var}` interpolation** (TASK-058)  
   Expands steps with `loop:` and interpolates `{var}` in workflow strings (also outside loops).
4. **Parameter resolution**  
   Resolves `$CALCULATE(...)`, `$AUTO_*`, and `$variable` in `params`.
5. **Condition evaluation + context simulation**  
   Evaluates `condition` and simulates step effects so later conditions see updated state.

The important consequence:

- **Adaptation is a filter BEFORE conditions.**
- **Loops expand BEFORE conditions.**
- **Conditions can still skip steps AFTER adaptation.**

---

## Two Filters: Adaptation vs `condition`

### Filter 1: Adaptation (TASK-051)

Adaptation decides which steps are even considered, before any runtime evaluation.

Rules (simplified):

- **HIGH** confidence → include **all** steps.
- **LOW / NONE** → include only **core** steps.
- **MEDIUM** → include core + relevant optional steps.

Definitions:

- **Core step**: `optional: false` OR `disable_adaptation: true`
- **Optional step**: `optional: true` AND `disable_adaptation: false`

For **MEDIUM** confidence, optional steps can be included by:

1. `tags` keyword match against prompt
2. custom boolean semantic filters (e.g. `add_bench: true`)
3. semantic similarity fallback (if enabled)

If a step is removed here, it will **never** run later (even if its `condition` would evaluate to `true`).

### Filter 2: `condition` (runtime evaluation)

After the pipeline expands loops and resolves params, each step can be skipped by:

```yaml
condition: "..."
```

Conditions can reference:

- scene context (e.g. `current_mode`, `has_selection`, `selected_verts`, …)
- workflow parameters (`defaults`, `modifiers`, computed params, explicit params)
- values produced by `{var}` interpolation (e.g. loop variable `{i}`)

So a step runs only if:

1) it survived adaptation selection, **and**  
2) its `condition` evaluated to `true`.

---

## Authoring Guidance (When to Use What)

### Use `optional: true` for “nice-to-have” features

Good examples:

- benches, decorations, handles
- extra detailing steps
- optional variants requested explicitly by user prompt

These can be safely omitted when the router is not confident.

### Use `condition` for deterministic logic based on params/context

Good examples:

- “only create plank if `{i} <= plank_count`”
- “only switch to EDIT if not already in EDIT”
- “only add braces if leg angle implies X-frame geometry”

### If a step must be controlled ONLY by `condition`, bypass adaptation

If the step is optional in meaning, but should not be dropped by semantic filtering (because the decision is purely mathematical/param-based), use:

```yaml
optional: true
disable_adaptation: true
condition: "..."
```

This keeps the step in the pipeline (treated as core), and lets `condition` decide at runtime.

---

## Example A: Prompt-Driven Optional Feature (benches)

Bench steps should appear only when the user asks for benches.

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE, name: "BenchLeft" }
  description: "Create bench"
  optional: true
  tags: ["bench", "seating"]
```

Behavior:

- user prompt mentions “bench” → step likely included at MEDIUM confidence
- user prompt does not mention “bench” → step filtered out early
- `condition` is usually not needed here

---

## Example B: Condition-Driven Variant (X-frame legs)

If a step depends on parameters (not prompt semantics), you usually want `condition` to be authoritative.

```yaml
- tool: mesh_transform_selected
  params:
    # Example param-based transform
    translate: ["$CALCULATE(0.1 if leg_style == 'x' else 0)", 0, 0]
  description: "Stretch leg top for X-frame"
  optional: true
  disable_adaptation: true
  condition: "leg_style == 'x'"
```

Behavior:

- step is not removed by adaptation (because `disable_adaptation: true`)
- it runs only if `leg_style == 'x'`

---

## Loops + Conditions: What to Expect

Loops expand first, so each iteration becomes a concrete step, and then conditions run per-iteration:

```yaml
- tool: modeling_create_primitive
  params:
    name: "Plank_{i}"
  loop:
    variable: i
    range: "1..plank_count"
  condition: "{i} <= plank_count"
```

Notes:

- `{i}` is interpolated before evaluation, so the condition becomes e.g. `"3 <= plank_count"`.
- if `{i}` or `{plank_count}` is missing in context, expansion fails (strict interpolation).

---

## Summary

- Adaptation is an **early step-selection filter** (prompt/intent safety).
- `condition` is a **runtime filter** (deterministic logic).
- If you need param-based branching, prefer `condition` and consider `disable_adaptation: true`.
- Loops/interpolation happen before `$CALCULATE` and before `condition`, so you can safely use `{i}` inside both.

