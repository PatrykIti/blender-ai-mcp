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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-088-03-01](./TASK-088-03-01_Core_Progress_Cancellation_Result_Retrieval.md) | Core Progress, Cancellation, and Result Retrieval | Core implementation layer |
| [TASK-088-03-02](./TASK-088-03-02_Tests_Progress_Cancellation_Result_Retrieval.md) | Tests and Docs Progress, Cancellation, and Result Retrieval | Tests, docs, and QA |

---

## Acceptance Criteria

- clients can observe progress and cancel work without restarting the session
