# TASK-088-06: Task Mode Tests, Operations, and Docs

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-088-05](./TASK-088-05_Background_Adoption_for_Imports_Renders_Extraction_and_Workflow_Import.md)

---

## Objective

Close the task-mode rollout with regression coverage, operations guidance, and documentation.

---

## Planned Work

- progress, timeout, and cancellation tests
- `TaskConfig` mode matrix tests (`forbidden` / `optional` / `required`)
- decorator registration guard test: `task=True` is accepted only on `async def`
- operations docs for job cleanup and stuck-task diagnosis
- updates to:
  - `_docs/_TESTS/README.md`
  - `_docs/_MCP_SERVER/README.md`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-088-06-01](./TASK-088-06-01_Core_Task_Mode_Operations_Docs.md) | Core Task Mode Tests, Operations, and Docs | Core implementation layer |
| [TASK-088-06-02](./TASK-088-06-02_Tests_Task_Mode_Operations_Docs.md) | Tests and Docs Task Mode Operations and Docs | Tests, docs, and QA |

---

## Acceptance Criteria

- task mode has test coverage and clear operating guidance
- task-mode semantics (`forbidden` / `optional` / `required`) are test-covered and documented per endpoint
- invalid sync registration with `task=True` is covered by a failing-registration test

## Completion Summary

- added focused tests for candidacy, registry/result bookkeeping, task-mode registration semantics, adopted tool paths, and addon-side background RPC lifecycle
- documented the first task-mode operating model in repo docs, MCP docs, and test docs
- registration guard coverage now proves that sync functions cannot be registered with task mode enabled
