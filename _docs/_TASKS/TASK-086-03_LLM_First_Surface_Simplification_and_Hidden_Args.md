# TASK-086-03: LLM-First Surface Simplification and Hidden Args

**Parent:** [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md)

---

## Objective

Hide backend-only arguments and expose only the parameters that an LLM should realistically provide on the `llm-guided` surface.

## Completion Summary

This slice is now closed.

- `llm-guided` hides avoidable technical noise on the high-value public tools already covered by the alias layer
- tests verify the current hidden-argument behavior
- docs/prompts now use the simplified public surface consistently for the currently-aliased tools

---

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/mesh.py`
- `server/adapters/mcp/areas/workflow_catalog.py`

---

## Planned Work

- classify parameters into:
  - public and required
  - public with safe defaults
  - expert-only
  - internal-only
- attach public-parameter profiles to surfaces

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-086-03-01](./TASK-086-03-01_Core_LLM_Simplification_Hidden_Args.md) | Core LLM-First Surface Simplification and Hidden Args | Core implementation layer |
| [TASK-086-03-02](./TASK-086-03-02_Tests_LLM_Simplification_Hidden_Args.md) | Tests and Docs LLM-First Surface Simplification and Hidden Args | Tests, docs, and QA |

---

## Acceptance Criteria

- the `llm-guided` surface no longer exposes avoidable technical noise
- expert and internal surfaces can still expose advanced controls where needed
