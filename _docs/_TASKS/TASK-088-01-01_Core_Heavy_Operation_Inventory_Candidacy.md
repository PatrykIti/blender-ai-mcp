# TASK-088-01-01: Core Heavy Operation Inventory and Task Candidacy

**Parent:** [TASK-088-01](./TASK-088-01_Heavy_Operation_Inventory_and_Task_Candidacy.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

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

- build a candidacy matrix for:
  - `scene_get_viewport`
  - `extraction_render_angles`
  - `workflow_catalog(import_finalize)`
  - import and export tools
  - future reconstruction tools
---

## Acceptance Criteria

- every heavy tool has an explicit execution mode classification
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
