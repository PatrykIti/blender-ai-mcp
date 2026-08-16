# TASK-092-07: Workflow Catalog Recovery Assistant Guidance

**Parent:** [TASK-092](./TASK-092_Server_Side_Sampling_Assistants.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-04](./TASK-092-04_Router_Integration_Masking_and_Budget_Control.md)

---

## Objective

Extend bounded recovery guidance to `workflow_catalog` import flows so conflict/error states can surface structured next-step assistance.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/adapters/mcp/contracts/workflow_catalog.py`
- `tests/unit/tools/workflow_catalog/`

---

## Target Tool

- `workflow_catalog`

Focus states:

- `needs_input`
- `skipped`
- explicit import/import-finalize errors

---

## Acceptance Criteria

- import-oriented workflow-catalog recovery states can attach bounded typed repair guidance
- guidance stays diagnostic and does not replace overwrite/clarification policy

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-092-07-01](./TASK-092-07-01_Core_Workflow_Catalog_Recovery_Assistant_Guidance.md) | Core Workflow Catalog Recovery Assistant Guidance | Core implementation layer |
| [TASK-092-07-02](./TASK-092-07-02_Tests_Workflow_Catalog_Recovery_Assistant_Guidance.md) | Tests and Docs Workflow Catalog Recovery Assistant Guidance | Tests, docs, and QA |
