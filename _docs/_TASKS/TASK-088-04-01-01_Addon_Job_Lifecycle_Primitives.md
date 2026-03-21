# TASK-088-04-01-01: Addon Job Lifecycle Primitives

**Parent:** [TASK-088-04-01](./TASK-088-04-01_Core_RPC_Blender_Main_Thread.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-04](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md)  

---

## Objective

Implement the **Addon Job Lifecycle Primitives** slice of the parent task.

---

## Repository Touchpoints

- `blender_addon/infrastructure/rpc_server.py`
- `blender_addon/application/handlers/system.py`
- `blender_addon/application/handlers/extraction.py`

---

## Planned Work

### Slice Outputs

- separate foreground and long-running operation boundaries with explicit contracts
- align RPC/task/pagination/timeout behavior with deterministic state transitions
- keep Blender main-thread safety and operational diagnostics explicit

### Implementation Checklist

- touch `blender_addon/infrastructure/rpc_server.py` with explicit change notes and boundary rationale
- touch `blender_addon/application/handlers/system.py` with explicit change notes and boundary rationale
- touch `blender_addon/application/handlers/extraction.py` with explicit change notes and boundary rationale
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
