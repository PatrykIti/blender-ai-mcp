# TASK-088-04-01-02: Server RPC Client and Protocol

**Parent:** [TASK-088-04-01](./TASK-088-04-01_Core_RPC_Blender_Main_Thread.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-04](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md)  

---

## Objective

Implement the **Server RPC Client and Protocol** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/rpc/client.py`

---

## Planned Work

### Slice Outputs

- expose explicit client methods for job lifecycle operations:
  - `launch`
  - `poll`
  - `cancel`
  - `collect_result`
- define deterministic protocol envelopes for request/response/error fields:
  - `request_id`
  - `job_id`
  - `status`
  - typed `error_code`
- keep backward compatibility for existing synchronous calls while routing new async-capable paths through explicit protocol verbs

### Implementation Checklist

- touch `server/adapters/rpc/client.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- client exposes explicit lifecycle methods for launch/poll/cancel/result retrieval
- protocol envelopes and error codes are deterministic and documented
- legacy synchronous operations remain usable during transition
- slice does not regress existing synchronous operations

---

## Atomic Work Items

1. Add explicit RPC client methods for `launch`, `poll`, `cancel`, and `collect_result`.
2. Implement typed envelope parsing and stable error mapping in the client adapter.
3. Add focused tests for lifecycle method behavior and protocol error handling.
4. Document verb contracts and compatibility behavior vs legacy sync calls.
