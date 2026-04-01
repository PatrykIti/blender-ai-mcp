# TASK-088-06-01: Core Task Mode Tests, Operations, and Docs

**Parent:** [TASK-088-06](./TASK-088-06_Task_Mode_Tests_Operations_and_Docs.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-088-05](./TASK-088-05_Background_Adoption_for_Imports_Renders_Extraction_and_Workflow_Import.md)

---

## Objective

Implement the core code changes for **Task Mode Tests, Operations, and Docs**.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_background_job_registry.py`
- `tests/unit/adapters/mcp/test_task_mode_registration.py`
- `tests/unit/adapters/mcp/test_task_mode_tools.py`
- `tests/unit/adapters/rpc/test_background_job_lifecycle.py`
- `_docs/_TESTS/README.md`
- `_docs/_MCP_SERVER/README.md`
---

## Planned Work

- progress, timeout, and cancellation tests
- operations docs for job cleanup and stuck-task diagnosis
- updates to:
  - `_docs/_TESTS/README.md`
  - `_docs/_MCP_SERVER/README.md`
---

## Acceptance Criteria

- task mode has test coverage and clear operating guidance
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.

## Completion Summary

- added focused task-mode regression coverage for registration guards, lifecycle bookkeeping, adopted tools, and addon-side control-plane verbs
- updated MCP/test docs with explicit task-mode operating guidance and validation commands
