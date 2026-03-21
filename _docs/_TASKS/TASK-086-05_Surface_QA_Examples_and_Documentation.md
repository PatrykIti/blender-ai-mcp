# TASK-086-05: Surface QA, Examples, and Documentation

**Parent:** [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-086-03](./TASK-086-03_LLM_First_Surface_Simplification_and_Hidden_Args.md), [TASK-086-04](./TASK-086-04_Compatibility_Adapters_and_Dispatcher_Alignment.md)

---

## Objective

Close the surface-optimization work with clarity-focused tests, examples, and documentation.

---

## Planned Work

- snapshot tests for public surface schemas
- update:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_PROMPTS/*`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-086-05-01](./TASK-086-05-01_Core_QA_Examples_Documentation.md) | Core Surface QA, Examples, and Documentation | Core implementation layer |
| [TASK-086-05-02](./TASK-086-05-02_Tests_QA_Examples_Documentation.md) | Tests and Docs Surface QA, Examples, and Documentation | Tests, docs, and QA |

---

## Acceptance Criteria

- docs and prompt examples use the new public surface consistently
- regressions in naming or parameter visibility are caught by tests
