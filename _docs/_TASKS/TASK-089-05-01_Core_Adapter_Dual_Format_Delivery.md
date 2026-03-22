# TASK-089-05-01: Core Adapter Dual-Format Delivery Strategy

**Parent:** [TASK-089-05](./TASK-089-05_Adapter_Dual_Format_Delivery_Strategy.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md), [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md)

---

## Objective

Implement the core code changes for **Native Structured-First Delivery and Compatibility Strategy**.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/output_schema.py`
- `server/adapters/mcp/contracts/compat.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `tests/unit/adapters/mcp/test_contract_base.py`

---

## Planned Work

- switch contract-enabled adapters from JSON-string returns to native object/model returns
- declare explicit `outputSchema` where needed for stable public contracts
- define profile/contract exceptions only where deterministic legacy text fallback is still required
- avoid introducing custom response renderers unless native FastMCP structured delivery proves insufficient

---

## Acceptance Criteria

- the transition to structured output does not force a destructive client cut-over
- structured surfaces expose contract-aligned `structuredContent` + `outputSchema`
- compatibility surfaces preserve deterministic text fallback without contract drift

---

## Atomic Work Items

1. Convert the first contract-enabled adapters to native object/model returns.
2. Add contract-line overrides only where legacy payloads must remain available.
3. Add adapter tests for native `structuredContent` + `outputSchema` alignment and backward compatibility.
