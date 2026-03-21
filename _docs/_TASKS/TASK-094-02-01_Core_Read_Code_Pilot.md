# TASK-094-02-01: Core Read-Only Code Mode Pilot Surface

**Parent:** [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** None

---

## Objective

Implement the core code changes for **Read-Only Code Mode Pilot Surface**.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`

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
