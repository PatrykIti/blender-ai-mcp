# TASK-089-05: Adapter Dual-Format Delivery Strategy

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md), [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md)

---

## Objective

Define the transition strategy for delivering structured-first responses while still supporting summary text and legacy clients where required.

---

## Planned Work

- add response renderers for:
  - `structured`
  - `structured_plus_summary`
  - `legacy_text`
- choose the renderer by surface profile or version

---

## Acceptance Criteria

- the transition to structured output does not force a destructive client cut-over
