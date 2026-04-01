# TASK-088-04: RPC and Blender Main-Thread Adaptation

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md), [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)

---

## Objective

Adapt RPC and addon runtime so longer-running work no longer depends on a single blocking request-response timeout while still preserving Blender main-thread safety.

---

## Repository Touchpoints

- `blender_addon/infrastructure/rpc_server.py`
- `server/adapters/rpc/client.py`
- `blender_addon/application/handlers/extraction.py`
- `blender_addon/application/handlers/system.py`

---

## Planned Work

- separate:
  - fast request-response calls
  - task launch
  - task polling or result retrieval
  - task cancellation
- replace the one-size-fits-all 30-second wait strategy by consuming the shared job-aware timeout policy defined in TASK-093-02

### RPC Shape Direction

Prefer explicit RPC verbs or payload types for:

- launch
- poll
- cancel
- collect result

Do not define a second timeout taxonomy in this task.
Timeout values, boundary names, and fallback semantics come from TASK-093-02 and are only applied here to the concrete RPC/addon runtime.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-088-04-01](./TASK-088-04-01_Core_RPC_Blender_Main_Thread.md) | Core RPC and Blender Main-Thread Adaptation | Core implementation layer |
| [TASK-088-04-02](./TASK-088-04-02_Tests_RPC_Blender_Main_Thread.md) | Tests and Docs RPC and Blender Main-Thread Adaptation | Tests, docs, and QA |

---

## Acceptance Criteria

- background jobs no longer depend on one blocking `result_queue.get(timeout=30.0)` model

## Completion Summary

- added explicit RPC verbs:
  - `rpc.launch_job`
  - `rpc.get_job`
  - `rpc.cancel_job`
  - `rpc.collect_job`
- addon runtime now keeps independent background job state instead of coupling long-running work to the foreground `result_queue.get(timeout=...)` path
- cooperative timeout/cancel checks now consume the shared timeout budget during background execution instead of inventing a parallel timeout taxonomy

---

## Atomic Work Items

1. Add addon-side job lifecycle primitives.
2. Add RPC client methods for launch, poll, cancel, and collect.
3. Keep Blender main-thread execution safe while decoupling job completion from socket wait time.
