# TASK-088-01-01: Core Heavy Operation Inventory and Task Candidacy

**Parent:** [TASK-088-01](./TASK-088-01_Heavy_Operation_Inventory_and_Task_Candidacy.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Implement the core code changes for **Heavy Operation Inventory and Task Candidacy**.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/extraction.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `blender_addon/infrastructure/rpc_server.py`
- `server/adapters/rpc/client.py`

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
