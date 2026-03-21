# TASK-093-02-01-02: RPC and Addon Timeout Coordination

**Parent:** [TASK-093-02-01](./TASK-093-02-01_Core_Timeout.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)  

---

## Objective

Implement the **RPC and Addon Timeout Coordination** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/rpc/client.py`
- `blender_addon/infrastructure/rpc_server.py`

---

## Planned Work

### Slice Outputs

- separate foreground and long-running operation boundaries with explicit contracts
- align RPC/task/pagination/timeout behavior with deterministic state transitions
- keep Blender main-thread safety and operational diagnostics explicit

### Implementation Checklist

- touch `server/adapters/rpc/client.py` with explicit change notes and boundary rationale
- touch `blender_addon/infrastructure/rpc_server.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- operation lifecycle states are explicit and test-covered
- timeouts/pagination/diagnostics behavior is boundary-specific and documented
- error and cancellation paths preserve consistent contracts
- slice does not regress existing synchronous operations

---

## Atomic Work Items

1. Implement operation boundary logic and contracts in listed touchpoints.
2. Add tests for launch/poll/cancel/timeout/pagination state transitions as applicable.
3. Capture baseline vs post-change operational metrics for the slice.
4. Document runtime boundary behavior and failure semantics.
