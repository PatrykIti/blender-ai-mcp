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
- choose the renderer by surface profile, contract line, or explicit compatibility override
- enforce MCP delivery parity:
  - structured renderers expose `structuredContent` and respect declared `outputSchema`
  - legacy renderer keeps text compatibility without changing source structured payloads

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-05-01](./TASK-089-05-01_Core_Adapter_Dual_Format_Delivery.md) | Core Adapter Dual-Format Delivery Strategy | Core implementation layer |
| [TASK-089-05-02](./TASK-089-05-02_Tests_Adapter_Dual_Format_Delivery.md) | Tests and Docs Adapter Dual-Format Delivery Strategy | Tests, docs, and QA |

---

## Acceptance Criteria

- the transition to structured output does not force a destructive client cut-over
- contract-enabled tools expose `structuredContent` + `outputSchema` on structured surfaces
- legacy text fallback remains available and deterministic on compatibility surfaces

---

## Atomic Work Items

1. Define default renderer selection per surface profile.
2. Add contract-line overrides where legacy payloads must remain available.
3. Add adapter tests for renderer selection and backward compatibility.
