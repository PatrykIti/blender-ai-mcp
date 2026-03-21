# TASK-089-05-01: Core Adapter Dual-Format Delivery Strategy

**Parent:** [TASK-089-05](./TASK-089-05_Adapter_Dual_Format_Delivery_Strategy.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md), [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md)

---

## Objective

Implement the core code changes for **Adapter Dual-Format Delivery Strategy**.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/renderers.py`
- `server/adapters/mcp/contracts/serializers.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `tests/unit/adapters/mcp/test_contract_base.py`
---

## Planned Work

- add response renderers for:
  - `structured`
  - `structured_plus_summary`
  - `legacy_text`
- choose the renderer by surface profile, contract line, or explicit compatibility override
- ensure structured renderers emit MCP `structuredContent` aligned to declared `outputSchema`
- ensure legacy renderer emits compatible text fallback from the same source structured payloads
---

## Acceptance Criteria

- the transition to structured output does not force a destructive client cut-over
- structured surfaces expose contract-aligned `structuredContent` + `outputSchema`
- compatibility surfaces preserve deterministic text fallback without contract drift
---

## Atomic Work Items

1. Define default renderer selection per surface profile.
2. Add contract-line overrides where legacy payloads must remain available.
3. Add adapter tests for renderer selection, `structuredContent` + `outputSchema` alignment, and backward compatibility.
