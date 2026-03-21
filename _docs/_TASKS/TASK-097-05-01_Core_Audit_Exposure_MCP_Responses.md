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

### Slice Outputs

- materialize structured execution/audit/postcondition behavior for correction paths
- ensure verification triggers map to inspection contracts for high-risk fixes
- expose auditable outcomes to responses/logs with deterministic fields

### Implementation Checklist

- touch `server/adapters/mcp/contracts/correction_audit.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/execution_report.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/router_helper.py` with explicit change notes and boundary rationale
- touch `server/router/infrastructure/logger.py` with explicit change notes and boundary rationale
- touch `server/infrastructure/telemetry.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- audit and execution-report fields are complete and deterministic
- postcondition verification gates high-risk success finalization
- failure/inconclusive verification paths are explicit and test-covered
- slice integrates with policy and contract layers without ambiguity

---

## Atomic Work Items

1. Implement audit/report/verification mapping in listed touchpoints.
2. Add tests for success, failure, and inconclusive verification outcomes.
3. Capture before/after audit payload examples for corrected executions.
4. Document postcondition trigger rules and exposure policy.
