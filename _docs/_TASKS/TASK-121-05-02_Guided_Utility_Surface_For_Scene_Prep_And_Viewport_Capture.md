# TASK-121-05-02: Guided Utility Surface for Scene Prep and Viewport Capture

**Parent:** [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Expose a bounded guided-safe utility path for preparing vision inputs inside
`llm-guided`, without reopening the whole legacy surface.

---

## Business Problem

Even when the router does not misclassify the goal, `llm-guided` still lacks a
practical utility path for:

- scene cleanup/reset
- viewport screenshot capture
- simple capture-prep steps before/after a workflow or macro

Because these tools are hidden in bootstrap/planning, search-first discovery
cannot reach them, and `call_tool(...)` cannot invoke them either.

This means the production-oriented surface cannot perform one of the most basic
tasks needed for `TASK-121`: preparing vision inputs.

---

## Implementation Direction

- define a small guided-safe utility set for:
  - scene cleanup/reset
  - viewport capture
- expose that set in the correct guided phases instead of hiding it behind the
  broader build escape hatch
- keep the utility set intentionally small and reversible
- prefer explicit visibility rules over ad hoc router-side heuristics

Possible surface shapes:

- allow a minimal subset of existing tools such as:
  - `scene_clean_scene`
  - `scene_get_viewport`
- or introduce one bounded helper surface/tool if that proves safer than
  exposing the raw utility primitives directly

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_phase.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

---

## Acceptance Criteria

- `llm-guided` has a bounded utility path for scene prep and viewport capture
- guided search can discover the exposed utility tools in the right phase
- the surface stays curated and does not regress toward legacy-flat breadth
