# TASK-097-05-01: Core Audit Exposure in MCP Responses and Logs

**Parent:** [TASK-097-05](./TASK-097-05_Audit_Exposure_in_MCP_Responses_and_Logs.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-097-02](./TASK-097-02_Router_Execution_Report_Pipeline.md), [TASK-097-04](./TASK-097-04_Inspection_Based_Verification_Integration.md)

---

## Objective

Implement the core code changes for **Audit Exposure in MCP Responses and Logs**.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/correction_audit.py`
- `server/adapters/mcp/execution_report.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/infrastructure/logger.py`
- `server/infrastructure/telemetry.py`
---

## Planned Work

### Deliverables

- implement the slice behavior end-to-end across: `server/adapters/mcp/contracts/correction_audit.py`, `server/adapters/mcp/execution_report.py`, `server/adapters/mcp/router_helper.py`, `server/router/infrastructure/logger.py`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `server/adapters/mcp/contracts/correction_audit.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/execution_report.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/router_helper.py` with an explicit change note (or explicit no-change rationale)
- touch `server/router/infrastructure/logger.py` with an explicit change note (or explicit no-change rationale)
- touch `server/infrastructure/telemetry.py` with an explicit change note (or explicit no-change rationale)
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
