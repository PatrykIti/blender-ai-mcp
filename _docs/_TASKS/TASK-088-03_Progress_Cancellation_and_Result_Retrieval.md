# TASK-088-03: Progress, Cancellation, and Result Retrieval

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md)

---

## Objective

Define a stable progress, cancellation, and result-retrieval model for background jobs.

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
