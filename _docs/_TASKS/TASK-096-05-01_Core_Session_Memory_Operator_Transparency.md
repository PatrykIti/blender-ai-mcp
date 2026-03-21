# TASK-096-05-01: Core Session Memory and Operator Transparency

**Parent:** [TASK-096-05](./TASK-096-05_Session_Memory_and_Operator_Transparency.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)

---

## Objective

Implement the core code changes for **Session Memory and Operator Transparency**.

---

## Repository Touchpoints

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/execution_report.py`
- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/contracts/router.py`
---

## Planned Work

### Deliverables

- implement the slice behavior end-to-end across: `server/adapters/mcp/session_state.py`, `server/adapters/mcp/execution_report.py`, `server/adapters/mcp/areas/router.py`, `server/application/tool_handlers/router_handler.py`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `server/adapters/mcp/session_state.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/execution_report.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/areas/router.py` with an explicit change note (or explicit no-change rationale)
- touch `server/application/tool_handlers/router_handler.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/contracts/router.py` with an explicit change note (or explicit no-change rationale)
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
