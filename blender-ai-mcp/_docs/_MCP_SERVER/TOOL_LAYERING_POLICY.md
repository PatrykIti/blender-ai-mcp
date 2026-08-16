# Tool Layering Policy

Canonical policy for the MCP product surface.

If another doc disagrees with this file about:

- what should be public vs hidden
- how tools are layered
- when `router_set_goal(...)` is expected
- how vision should be used
- what counts as the truth layer

this file wins.

---

## Purpose

The repo no longer treats the full flat tool catalog as the preferred public
LLM interface.

The product direction is now:

- keep low-level power available internally
- expose a smaller, more meaningful public action space
- make normal LLM usage goal-first
- use vision as interpretation support
- use deterministic measurement/assertion as the truth layer

This policy exists so contributors do not need to reconstruct the intended tool
model from old tasks, old prompts, or scattered notes.

---

## Ownership

This file is the canonical policy source for:

- tool layering (`atomic` / `macro` / `workflow`)
- public-surface exposure rules
- hidden atomic layer rules
- goal-first orchestration rules
- vision vs measure/assert boundaries
- historical supersession notation

The following docs should defer to this file instead of redefining policy:

- [README.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/README.md)
- [_docs/_MCP_SERVER/README.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/_docs/_MCP_SERVER/README.md)
- [_docs/AVAILABLE_TOOLS_SUMMARY.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/_docs/AVAILABLE_TOOLS_SUMMARY.md)
- [ARCHITECTURE.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/ARCHITECTURE.md)
- [_docs/_DEV/README.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/_docs/_DEV/README.md)

These other docs remain important, but they are reference/inventory/implementation docs, not the policy source.

---

## Core Terms

### Atomic Tool

Small, deterministic, precise, individually testable.

Atomic tools exist mainly as:

- implementation substrate
- internal/debug power layer
- building blocks for macro/workflow tools

Atomic tools should not be the default public interface on production-oriented LLM surfaces.

### Macro Tool

A task-oriented tool built from atomic tools that still has one clear responsibility.

Macro tools are the preferred default public working layer for normal LLM usage.

Macro-tool rules:

- one meaningful task responsibility
- may orchestrate atomic tools internally
- should return task-relevant structured outputs
- should be understandable in one sentence
- should not expand into open-ended process engines

### Workflow Tool

A bounded process tool that orchestrates macro tools, atomic tools, rules,
verification, and optionally vision before/after analysis.

A workflow tool is not an open-ended “do anything” tool.

Workflow/mega-tool rules:

- must remain bounded
- may orchestrate:
  - atomic tools
  - macro tools
  - rules/policy checks
  - before/after capture
  - measure/assert calls
  - vision interpretation
- must return a structured report describing:
  - what was attempted
  - what changed
  - what passed
  - what failed
  - recommended next step when verification fails

### Public Surface

The intentionally exposed MCP catalog for a given profile/surface.

Public surfaces are product decisions, not accidental byproducts of what exists internally.

### Hidden Atomic Layer

Low-level/internal tools that may exist and remain usable by maintainers or
specialized execution paths, but are not part of the normal public LLM-facing catalog.

### Truth Layer

Deterministic measurement/assertion and inspection.

Vision is not the final authority on correctness.

---

## Product Rules

### 1. Small Public Catalogs

Production-oriented LLM surfaces should expose:

- workflow tools
- macro tools
- a very small number of essential single-purpose tools

They should not expose the entire low-level catalog by default.

### 2. Hidden Atomic Layer by Default

Atomic tools should be hidden for most normal LLM-facing surfaces unless there
is a specific escape-hatch reason to expose them.

Hidden atomic tools may still be:

- used internally by macro/workflow tools
- exposed on maintainer/debug surfaces
- reachable through narrowly-scoped compatibility or internal execution paths

But they should not define the normal public product surface.

### 2a. Discovery Must Respect The Hidden Atomic Layer

Discovery/search must not behave as if every internal tool is a normal public
candidate.

Rules:

- prefer workflow/macro tools ahead of raw atomic tools
- do not leak hidden atomic tools into normal bootstrap catalogs
- if an atomic tool is discoverable publicly at all, that must be an explicit
  exception rather than the default behavior

### 2b. Escape Hatches Must Be Explicit

Some single-purpose tools are still worth exposing publicly.

Typical public escape hatches:

- `router_set_goal`
- `router_get_status`
- essential truth/inspection tools
- explicit measure/assert tools as they are introduced
- a very small number of operational recovery tools where the product value
  clearly outweighs the surface-cost

These are exceptions to the layering model, not evidence that the atomic layer
should stay broadly public.

### 3. Goal-First by Default

Normal LLM production surfaces should begin from `router_set_goal(...)`.

The server should know:

- what the LLM is trying to do
- which phase it is in
- what kind of verification or visual interpretation should apply

For normal production-oriented LLM surfaces, `router_set_goal(...)` should be
treated as the required session bootstrap unless the surface is explicitly
documented as an exception.

Current exception surfaces that may legitimately skip strict goal-first usage:

- maintainer/debug surfaces
- narrow manual/test surfaces
- experimental non-production surfaces with a different documented model

### 4. Vision Is Support, Not Truth

Vision can help:

- summarize what changed
- localize likely issues
- compare before/after views

Vision must not replace deterministic inspection/measurement/assertion when correctness matters.

### 4b. Before/After Capture Is A Platform Pattern

For meaningful visual verification flows, the preferred pattern is:

1. before capture
2. action/change
3. after capture
4. structured compare/summary

The view set should be consistent and intentional. Typical standard views:

- front
- side
- top
- iso
- focus-target view when needed

### 4c. Measurement/Assertion Is The Truth Layer

The expected deterministic verification family should cover at least:

- dimensions
- distance
- gap/contact
- overlap/intersection
- alignment
- proportion
- symmetry
- containment

Vision may help interpret and localize problems, but deterministic
measurement/assertion should remain the final truth source.

### 4d. Lightweight Vision Model Guidance

Lightweight vision models are acceptable when the task is:

- compare before/after views
- summarize visible changes
- localize likely visual issues
- provide compact human/LLM-readable interpretation

They should not be treated as the final authority on geometric correctness when
measure/assert tools can answer the question directly.

### 4a. Session Context Must Survive Beyond The Initial Goal Call

Once a goal is set, later tools and analysis layers should be able to rely on a
minimal session context contract:

- active goal / user intent
- current modeling phase
- current target object/component when known
- expected verification criteria
- the frame of reference for before/after visual analysis

This context is part of the product contract, not an incidental side-effect of
router internals.

### 5. Mega Tools Must Be Bounded

“Mega tool” is acceptable only when it represents a bounded domain/process.

It must not become a giant ambiguous catch-all tool.

### 6. Business Intent vs Legacy Form

Old task docs may still describe valid business goals while using obsolete tool-surface assumptions.

When that happens, mark them as superseded in form, not necessarily obsolete in business value.

---

## Surface Matrix

This is the intended product posture for the current known surfaces.

| Surface | Public Layer | Goal-First | Intended Use |
|---|---|---|---|
| `legacy-manual` | broad manual/control surface | no | maintainer/manual operation, troubleshooting, direct low-level access |
| `legacy-flat` | compatibility/control surface | optional | compatibility clients, broad control, legacy behavior |
| `llm-guided` | small curated public catalog | yes | normal production LLM usage |
| `internal-debug` | debug/maintainer surface | optional | diagnostics, maintainer access, broader internals |
| `code-mode-pilot` | experimental read-only analytical surface | no | analysis-heavy experiments, not normal write/destructive production use |

Interpretation:

- `llm-guided` is the main product surface for normal LLM usage
- `legacy-*` surfaces are not the target model for long-term product ergonomics
- `internal-debug` and `legacy-manual` may expose much more than normal production surfaces

---

## Documentation Notation

When an old doc is no longer architecturally current:

- prefer a visible banner such as:
  - `Status: ⛔ Superseded by TASK-113`
- preserve the old content if it is historically useful
- do not silently rewrite old docs to pretend the old plan never existed
- use strike-throughs sparingly
- prefer a short supersession note with a backlink to the current policy/task

---

## Immediate Implications

Until the rest of `_docs/` is migrated:

- treat this file as the policy source
- treat older task docs that assume flat public exposure as historical
- do not design new public surfaces around the “everything visible” model
- design new tool families assuming:
  - hidden atomic layer
  - macro/workflow-first public surface
  - goal-first orchestration
  - vision + measure/assert cooperation
