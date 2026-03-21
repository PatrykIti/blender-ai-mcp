# TASK-097-02: Router Execution Report Pipeline

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)

---

## Objective

Extend router output and `route_tool_call()` so multi-step execution produces a structured execution report instead of only a concatenated text response.

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`
- `server/router/infrastructure/logger.py`

---

## Atomic Work Items

1. Define one execution-report schema shared by router-aware tool entry points.
2. Capture original call, corrected steps, executed steps, and final status.
3. Add adapter rendering tests for structured and summary variants.

### Boundary Rule

This task owns report pipeline structure and propagation.
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
