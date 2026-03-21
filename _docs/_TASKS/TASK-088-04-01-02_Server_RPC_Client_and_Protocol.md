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

### Deliverables

- implement the slice behavior end-to-end across: `server/adapters/rpc/client.py`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `server/adapters/rpc/client.py` with an explicit change note (or explicit no-change rationale)
- add or update focused regression coverage for the changed slice behavior
- capture one before/after example of the affected runtime surface (payload, config, or execution flow)

### Review Notes To Attach

- short rationale for every changed touchpoint
- explicit note of any deferred work (if present) and why it is safe to defer
- exact test commands used for slice validation

---

## Acceptance Criteria

- every listed touchpoint is either updated or explicitly marked as no-change with justification
- the slice has at least one focused regression test proving intended behavior
- no boundary violations are introduced relative to `RESPONSIBILITY_BOUNDARIES.md`
- parent-level behavior remains compatible when this slice lands alone

---

## Atomic Work Items

1. Implement the scoped behavior in the listed touchpoints with explicit boundary ownership.
2. Add/adjust regression tests for the changed behavior and verify deterministic outcomes.
3. Record before/after evidence for the changed surface (contract, visibility, routing, or runtime behavior).
4. Document any deferred edges and why they do not block parent-task acceptance.
