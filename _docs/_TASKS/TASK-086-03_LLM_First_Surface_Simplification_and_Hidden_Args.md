# TASK-086-03: LLM-First Surface Simplification and Hidden Args

**Parent:** [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md)

---

## Objective

Hide backend-only arguments and expose only the parameters that an LLM should realistically provide on the `llm-guided` surface.

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
