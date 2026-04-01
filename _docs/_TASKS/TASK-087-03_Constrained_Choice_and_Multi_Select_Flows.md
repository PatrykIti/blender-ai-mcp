# TASK-087-03: Constrained Choice and Multi-Select Flows

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md)

---

## Objective

Support enums, booleans, lists, and multi-select flows as typed elicitation widgets instead of relying on free-form text answers.

---

## Repository Touchpoints

- `server/router/domain/entities/parameter.py`
- workflow definitions in `server/router/application/workflows/custom/*.yaml`

---

## Planned Work

- map:
  - `enum` -> single choice
  - `bool` -> yes or no
  - `list[str]` -> multi-select
  - ranged numeric values -> validated numeric input

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-087-03-01](./TASK-087-03-01_Core_Constrained_Choice_Multi_Select.md) | Core Constrained Choice and Multi-Select Flows | Core implementation layer |
| [TASK-087-03-02](./TASK-087-03-02_Tests_Constrained_Choice_Multi_Select.md) | Tests and Docs Constrained Choice and Multi-Select Flows | Tests, docs, and QA |

---

## Acceptance Criteria

- enum parameters do not need to be typed manually as raw strings
- multi-select is supported for feature packs or export bundles
