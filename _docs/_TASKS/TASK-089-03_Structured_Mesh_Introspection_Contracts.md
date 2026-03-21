# TASK-089-03: Structured Mesh Introspection Contracts

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Standardize contracts for `mesh_inspect` and the internal `mesh_get_*` actions, including paging fields for large payloads.

---

## Repository Touchpoints

- `server/application/tool_handlers/mesh_handler.py`
- `server/adapters/mcp/areas/mesh.py`
- `server/domain/tools/mesh.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/contracts/mesh.py`
  - `tests/unit/tools/mesh/test_mesh_contracts.py`
- standardize an envelope with fields such as:
  - `object_name`
  - `offset`
  - `limit`
  - `returned`
  - `total`
  - `items`

---

## Acceptance Criteria

- mesh introspection contracts are consistent across all action types
- pagination fields are standardized
