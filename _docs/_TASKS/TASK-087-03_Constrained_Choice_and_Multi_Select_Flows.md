# TASK-087-03: Constrained Choice and Multi-Select Flows

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ⬜ Planned  
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

## Acceptance Criteria

- enum parameters do not need to be typed manually as raw strings
- multi-select is supported for feature packs or export bundles
