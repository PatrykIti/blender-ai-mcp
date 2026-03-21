# TASK-086-03-01: Core LLM-First Surface Simplification and Hidden Args

**Parent:** [TASK-086-03](./TASK-086-03_LLM_First_Surface_Simplification_and_Hidden_Args.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md)

---

## Objective

Implement the core code changes for **LLM-First Surface Simplification and Hidden Args**.

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

## Acceptance Criteria

- the `llm-guided` surface no longer exposes avoidable technical noise
- expert and internal surfaces can still expose advanced controls where needed
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
