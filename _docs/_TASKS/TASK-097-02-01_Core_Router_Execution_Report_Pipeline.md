# TASK-097-02-01: Core Router Execution Report Pipeline

**Parent:** [TASK-097-02](./TASK-097-02_Router_Execution_Report_Pipeline.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)

---

## Objective

Implement the core code changes for **Router Execution Report Pipeline**.

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`
- `server/router/infrastructure/logger.py`

---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- multi-step execution is represented as structured data as well as optional summary text
---

## Atomic Work Items

1. Define one execution-report schema shared by router-aware tool entry points.
2. Capture original call, corrected steps, executed steps, and final status.
3. Add adapter rendering tests for structured and summary variants.