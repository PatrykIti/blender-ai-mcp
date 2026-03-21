# TASK-094-02-01: Core Read-Only Code Mode Pilot Surface

**Parent:** [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md)

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

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- the pilot surface does not expose direct destructive write paths by default
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
