# TASK-086-03-01: Core LLM-First Surface Simplification and Hidden Args

**Parent:** [TASK-086-03](./TASK-086-03_LLM_First_Surface_Simplification_and_Hidden_Args.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

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

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
