# TASK-088-01: Heavy Operation Inventory and Task Candidacy

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Classify which operations should remain foreground, which should support optional background execution, and which should require task mode.

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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-088-01-01](./TASK-088-01-01_Core_Heavy_Operation_Inventory_Candidacy.md) | Core Heavy Operation Inventory and Task Candidacy | Core implementation layer |
| [TASK-088-01-02](./TASK-088-01-02_Tests_Heavy_Operation_Inventory_Candidacy.md) | Tests and Docs Heavy Operation Inventory and Task Candidacy | Tests, docs, and QA |

---

## Acceptance Criteria

- every heavy tool has an explicit execution mode classification

## Completion Summary

- added a shared candidacy matrix in `server/adapters/mcp/tasks/candidacy.py`
- classified the adopted first-wave endpoints (`scene_get_viewport`, `extraction_render_angles`, `workflow_catalog.import_finalize`) as `task_optional`
- classified import/export paths explicitly as deferred foreground-only entries for the next rollout wave
