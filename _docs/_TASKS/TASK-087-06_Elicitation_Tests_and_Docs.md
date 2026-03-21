# TASK-087-06: Elicitation Tests and Docs

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-03](./TASK-087-03_Constrained_Choice_and_Multi_Select_Flows.md), [TASK-087-04](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md), [TASK-087-05](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md)

---

## Objective

Add test coverage and documentation for both native elicitation mode and tool-only fallback mode.

---

## Planned Work

- unit contract tests
- router handler tests
- compatibility tests for fallback clients
- docs updates in:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `README.md`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-087-06-01](./TASK-087-06-01_Core_Elicitation_Tests_Docs.md) | Core Elicitation Tests and Docs | Core implementation layer |
| [TASK-087-06-02](./TASK-087-06-02_Tests_Elicitation_Tests_Docs.md) | Tests and Docs Elicitation Tests and Docs | Tests, docs, and QA |

---

## Acceptance Criteria

- both interaction modes are documented and regression-tested
