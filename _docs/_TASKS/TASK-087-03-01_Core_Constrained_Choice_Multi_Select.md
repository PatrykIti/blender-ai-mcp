# TASK-087-03-01: Core Constrained Choice and Multi-Select Flows

**Parent:** [TASK-087-03](./TASK-087-03_Constrained_Choice_and_Multi_Select_Flows.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md)

---

## Objective

Implement the core code changes for **Constrained Choice and Multi-Select Flows**.

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
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
