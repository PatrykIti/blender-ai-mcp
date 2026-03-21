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

### Spatial Priority

These contracts should make it easy for an LLM to stay oriented in mesh space:

- element identity
- coordinates
- connectivity
- selection flags
- layer or attribute names
- paging metadata

---

## Acceptance Criteria

- mesh introspection contracts are consistent across all action types
- pagination fields are standardized

---

## Atomic Work Items

1. Standardize envelope fields for all `mesh_inspect` actions.
2. Normalize per-item schemas for vertices, edges, faces, normals, UVs, attributes, shape keys, and weights.
3. Add paging and selection-filter tests for every action family.
