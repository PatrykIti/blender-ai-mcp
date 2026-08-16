# TASK-123-02: Local Background Task Terminality After Timeout

**Parent:** [TASK-123](./TASK-123_Runtime_Reliability_Fixes_For_Vision_Provider_Startup_And_Task_Terminality.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md), [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)

**Completion Summary:** The local background-task path now treats terminal outcomes as monotonic. Late progress callbacks are ignored once timeout/cancel/completion has made the task terminal, registry bookkeeping no longer lets `running` overwrite terminal states, and focused regression tests cover both the registry rule and a real timeout-plus-late-progress bridge scenario.

---

## Objective

Make timeout and other terminal outcomes for server-local background tasks
monotonic, even if the worker thread keeps running long enough to emit late
progress callbacks.

---

## Business Problem

`asyncio.wait_for(...)` stops awaiting the thread-backed local background
executor, but it does not kill the underlying worker thread created through
`asyncio.to_thread(...)`.

That means the current sequence can be:

1. task exceeds `MCP_TASK_TIMEOUT_SECONDS`
2. bridge marks the task as failed
3. worker thread continues running
4. a later `progress_callback(...)` reports `status="running"`
5. registry progress update overwrites the previous terminal failure

The result is operationally wrong:

- task polling can move from `failed` back to `running`
- diagnostics no longer reflect the real terminal outcome
- a timeout stops being a trustworthy product signal

---

## Repository Touchpoints

- `server/adapters/mcp/tasks/task_bridge.py`
- `server/adapters/mcp/tasks/job_registry.py` if a small terminal-state helper
  or monotonic guard is needed
- `tests/unit/adapters/mcp/test_task_mode_tools.py`
- `tests/unit/adapters/mcp/test_background_job_registry.py` if registry
  semantics change

---

## Implementation Direction

- keep terminal states monotonic once a task is `failed`, `cancelled`, or
  `completed`
- set the cooperative cancellation flag on timeout before any later callback can
  keep pretending the task is active
- ignore or no-op late progress updates after a terminal state is reached
- centralize the terminal-status rule in one helper if the same guard is needed
  in more than one place
- do not treat hard thread termination as part of this fix; the safety boundary
  is terminal-state integrity, not process/thread preemption

---

## Acceptance Criteria

- a timed-out local background task remains `failed`
- a late progress callback cannot change `failed` back to `running`
- the same terminal-state protection applies to `cancelled` and `completed`
  outcomes if late callbacks arrive
- task polling and diagnostics remain consistent with the first terminal outcome

---

## Leaf Work Items

1. Terminal-state guard
   - add a monotonic terminal-state rule in the bridge and/or shared registry
   - ensure late progress callbacks respect the task's terminal outcome
2. Regression coverage
   - add a regression test for timeout followed by late progress
   - add follow-up coverage for cancelled/completed late-callback cases if the
     guard is shared across terminal states
