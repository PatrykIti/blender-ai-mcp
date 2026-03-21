# TASK-097-04-01: Core Inspection-Based Verification Integration

**Parent:** [TASK-097-04](./TASK-097-04_Inspection_Based_Verification_Integration.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md), [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)  

---

## Objective

Implement the core code changes for **Inspection-Based Verification Integration**.

---

## Repository Touchpoints

- `server/router/application/router.py`
- `server/router/application/engines/tool_correction_engine.py`
- `server/router/adapters/mcp_integration.py`
- `server/adapters/mcp/router_helper.py`

---

## Planned Work

### Deliverables

- implement the slice behavior end-to-end across: `server/router/application/router.py`, `server/router/application/engines/tool_correction_engine.py`, `server/router/adapters/mcp_integration.py`, `server/adapters/mcp/router_helper.py`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `server/router/application/router.py` with an explicit change note (or explicit no-change rationale)
- touch `server/router/application/engines/tool_correction_engine.py` with an explicit change note (or explicit no-change rationale)
- touch `server/router/adapters/mcp_integration.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/router_helper.py` with an explicit change note (or explicit no-change rationale)
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
