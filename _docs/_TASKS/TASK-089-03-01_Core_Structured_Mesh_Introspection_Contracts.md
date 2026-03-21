# TASK-089-03-01: Core Structured Mesh Introspection Contracts

**Parent:** [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Implement the core code changes for **Structured Mesh Introspection Contracts**.

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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-03-01-01](./TASK-089-03-01-01_Mesh_Contract_Envelopes_and_Schemas.md) | Mesh Contract Envelopes and Schemas | Core slice |
| [TASK-089-03-01-02](./TASK-089-03-01-02_Handler_and_Paging_Integration.md) | Handler and Paging Integration | Core slice |

---

## Acceptance Criteria

- mesh introspection contracts are consistent across all action types
- pagination fields are standardized
---

## Atomic Work Items

1. Standardize envelope fields for all `mesh_inspect` actions.
2. Normalize per-item schemas for vertices, edges, faces, normals, UVs, attributes, shape keys, and weights.
3. Add paging and selection-filter tests for every action family.