# TASK-088-03-01: Core Progress, Cancellation, and Result Retrieval

**Parent:** [TASK-088-03](./TASK-088-03_Progress_Cancellation_and_Result_Retrieval.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md)

---

## Objective

Implement the core code changes for **Progress, Cancellation, and Result Retrieval**.

---

## Repository Touchpoints

- `server/adapters/mcp/tasks/progress.py`
- `server/adapters/mcp/tasks/result_store.py`
- `server/adapters/mcp/tasks/job_registry.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/extraction.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
---

## Planned Work

- create:
  - `server/adapters/mcp/tasks/progress.py`
  - `server/adapters/mcp/tasks/result_store.py`
- standardize fields such as:
  - `status`
  - `progress`
  - `status_message`
  - `result_ref`
  - `cancelled`
---

## Acceptance Criteria

- clients can observe progress and cancel work without restarting the session
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
