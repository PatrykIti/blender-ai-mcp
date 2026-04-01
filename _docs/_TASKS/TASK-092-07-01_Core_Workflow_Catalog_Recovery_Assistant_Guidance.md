# TASK-092-07-01: Core Workflow Catalog Recovery Assistant Guidance

**Parent:** [TASK-092-07](./TASK-092-07_Workflow_Catalog_Recovery_Assistant_Guidance.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

---

## Objective

Implement bounded repair-suggestion attachment for `workflow_catalog` import flows.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/adapters/mcp/contracts/workflow_catalog.py`

---

## Acceptance Criteria

- `workflow_catalog(import*)` recovery states can attach typed repair guidance
- repair guidance is request-bound and policy-subordinate
