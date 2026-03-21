# TASK-089-01-01: Core Contract Catalog and Response Guidelines

**Parent:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md)

---

## Objective

Implement the core code changes for **Contract Catalog and Response Guidelines**.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/__init__.py`
- `server/adapters/mcp/contracts/base.py`
- `server/adapters/mcp/contracts/serializers.py`
- `server/adapters/mcp/contracts/renderers.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/router_helper.py`
- `tests/unit/adapters/mcp/test_contract_base.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/contracts/__init__.py`
  - `server/adapters/mcp/contracts/base.py`
  - `server/adapters/mcp/contracts/serializers.py`
  - `server/adapters/mcp/contracts/renderers.py`
  - `tests/unit/adapters/mcp/test_contract_base.py`
---

## Acceptance Criteria

- the adapter layer has one shared response-design policy instead of per-tool conventions
---

## Atomic Work Items

1. Define one base response envelope that can carry structured payload, optional summary text, rendering metadata, and stable error fields.
2. Keep handlers returning Python data structures or domain entities; serialization and rendering stay in the adapter layer.
3. Add renderer selection by surface profile or explicit compatibility override without reintroducing per-tool formatting policy drift.
