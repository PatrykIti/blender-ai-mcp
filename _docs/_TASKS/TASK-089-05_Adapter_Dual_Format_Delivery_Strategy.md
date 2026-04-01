# TASK-089-05: Native Structured-First Delivery and Compatibility Strategy

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md), [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md)

---

## Objective

Define the transition strategy for delivering structured-first responses by relying on FastMCP's native structured/tool-output behavior first, while preserving explicit compatibility exceptions where required.

## Completion Summary

This slice is now closed.

- native structured-first delivery is the default on contract-enabled paths
- compatibility exceptions remain explicit and narrow instead of being spread across adapters
- tests cover both structured and compatibility delivery expectations

---

## Planned Work

- document which contract-enabled tools can rely on FastMCP automatic structured delivery immediately
- define where explicit `outputSchema` is required versus where object-like returns are sufficient
- define narrow compatibility exceptions for legacy text-heavy clients still expecting string output
- avoid introducing a custom renderer layer unless a concrete compatibility gap remains after native structured returns are in place

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
- legacy text fallback remains available and deterministic on compatibility surfaces where it is still needed
- first-pass rollout does not depend on a custom response-renderer subsystem

---

## Atomic Work Items

1. Audit which tools can switch from JSON-string returns to native object/model returns with no client breakage.
2. Define contract-line or profile-level exceptions only for the few tools that still need legacy text compatibility.
3. Add adapter tests for native structured delivery and backward compatibility.
