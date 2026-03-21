# TASK-097-02: Router Execution Report Pipeline

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md), [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)

---

## Objective

Extend the base execution report from TASK-089-04 so router output and `route_tool_call()` carry correction audit and verification-aware data instead of only a concatenated text response.

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`
- `server/router/infrastructure/logger.py`
- `server/infrastructure/di.py`

---

## Atomic Work Items

1. Reuse the base execution-report contract from TASK-089-04 instead of redefining it.
2. Add correction-audit fields and references to the correction event model from TASK-097-01.
3. Extend execution reporting with verification-ready status fields and placeholders that later subtasks can populate.
4. Add adapter rendering tests for structured and summary variants.

### Boundary Rule

TASK-089-04 owns the base report envelope and router/workflow response contracts.
This task owns only the audit/postcondition-oriented extension layer and propagation through the router-aware call path.
Postcondition trigger logic and inspection verification orchestration remain in:

- [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md)
- [TASK-097-04](./TASK-097-04_Inspection_Based_Verification_Integration.md)

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-097-02-01](./TASK-097-02-01_Core_Router_Execution_Report_Pipeline.md) | Core Router Execution Report Pipeline | Core implementation layer |
| [TASK-097-02-02](./TASK-097-02-02_Tests_Router_Execution_Report_Pipeline.md) | Tests and Docs Router Execution Report Pipeline | Tests, docs, and QA |

---

## Acceptance Criteria

- multi-step execution is represented as structured data as well as optional summary text
- the extended audit/verification fields remain backward-compatible with the base execution-report contract from TASK-089-04
