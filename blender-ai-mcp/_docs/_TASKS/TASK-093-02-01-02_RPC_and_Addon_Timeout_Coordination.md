# TASK-093-02-01-02: RPC and Addon Timeout Coordination

**Parent:** [TASK-093-02-01](./TASK-093-02-01_Core_Timeout.md)  
**Status:** ✅ Done  
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

- define one timeout budget hierarchy across boundaries:
  - FastMCP tool/task timeout
  - RPC client deadline
  - addon execution budget
- propagate deadlines explicitly from server RPC calls to addon execution paths
- normalize timeout and cancellation outcomes so clients receive stable boundary-specific errors

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

- timeout hierarchy is explicit, deterministic, and documented per boundary
- deadline propagation between RPC client and addon runtime is test-covered
- timeout errors are normalized into stable client-visible outcomes
- slice does not regress existing synchronous operations

---

## Atomic Work Items

1. Implement timeout budget fields and precedence rules in RPC client and addon runtime.
2. Add deadline propagation from RPC requests to addon task execution and polling paths.
3. Add tests for timeout-expired, timeout-inherited, and cancel-vs-timeout race scenarios.
4. Document boundary-specific timeout defaults and error mapping semantics.
