# TASK-097-05: Audit Exposure in MCP Responses and Logs

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-097-02](./TASK-097-02_Router_Execution_Report_Pipeline.md), [TASK-097-04](./TASK-097-04_Inspection_Based_Verification_Integration.md)

---

## Objective

Expose correction audit trails both to MCP clients and to platform telemetry or logging layers.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-097-05-01](./TASK-097-05-01_Core_Audit_Exposure_MCP_Responses.md) | Core Audit Exposure in MCP Responses and Logs | Core implementation layer |
| [TASK-097-05-02](./TASK-097-05-02_Tests_Audit_Exposure_MCP_Responses.md) | Tests and Docs Audit Exposure in MCP Responses and Logs | Tests, docs, and QA |

---

## Acceptance Criteria

- maintainers and operators can inspect what was changed and why
