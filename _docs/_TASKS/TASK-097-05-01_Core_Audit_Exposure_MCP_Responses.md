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

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- maintainers and operators can inspect what was changed and why
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
