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
- `server/adapters/mcp/contracts/output_schema.py`
- `server/adapters/mcp/contracts/compat.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/router_helper.py`
- `tests/unit/adapters/mcp/test_contract_base.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/contracts/__init__.py`
  - `server/adapters/mcp/contracts/base.py`
  - `server/adapters/mcp/contracts/output_schema.py`
  - `server/adapters/mcp/contracts/compat.py`
  - `tests/unit/adapters/mcp/test_contract_base.py`
- define native return-shape rules for adapters:
  - object-like returns by default for contract-enabled tools
  - explicit `outputSchema` where needed
  - explicit compatibility helpers only where legacy clients still require text-oriented behavior

---

## Acceptance Criteria

- the adapter layer has one shared response-design policy instead of per-tool conventions
- contract-enabled adapters do not depend on a custom renderer framework to expose structured state

---

## Atomic Work Items

1. Define one base response envelope and return-shape policy for contract-enabled tools.
2. Keep handlers returning Python data structures or domain entities; contract normalization stays in the adapter layer.
3. Remove JSON-string return patterns from the first contract-enabled tools.
4. Add tests proving native object/model returns surface correctly through FastMCP structured delivery.
