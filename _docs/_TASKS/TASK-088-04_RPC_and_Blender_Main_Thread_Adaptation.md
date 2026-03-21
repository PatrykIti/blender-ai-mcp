# TASK-088-04: RPC and Blender Main-Thread Adaptation

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md)

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
- replace the one-size-fits-all 30-second wait strategy with job-aware timeout policy

### RPC Shape Direction

Prefer explicit RPC verbs or payload types for:

- launch
- poll
- cancel
- collect result

---

## Acceptance Criteria

- background jobs no longer depend on one blocking `result_queue.get(timeout=30.0)` model

---

## Atomic Work Items

1. Add addon-side job lifecycle primitives.
2. Add RPC client methods for launch, poll, cancel, and collect.
3. Keep Blender main-thread execution safe while decoupling job completion from socket wait time.
