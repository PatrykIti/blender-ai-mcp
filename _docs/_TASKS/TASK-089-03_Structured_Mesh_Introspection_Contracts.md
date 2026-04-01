# TASK-089-03: Structured Mesh Introspection Contracts

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Standardize contracts for `mesh_inspect` and the internal `mesh_get_*` actions, including paging fields for large payloads.

## Completion Summary

This slice is now closed.

- `mesh_inspect` uses one consistent envelope across action families
- paging metadata and summary/item payload conventions are standardized
- tests cover contract validation and structured delivery on the MCP surface

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
- replace `json.dumps(...)` adapter returns in `mesh_inspect` actions with native structured payloads

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
| [TASK-089-03-01](./TASK-089-03-01_Core_Structured_Mesh_Introspection_Contracts.md) | Core Structured Mesh Introspection Contracts | Core implementation layer |
| [TASK-089-03-02](./TASK-089-03-02_Tests_Structured_Mesh_Introspection_Contracts.md) | Tests and Docs Structured Mesh Introspection Contracts | Tests, docs, and QA |

---

## Acceptance Criteria

- mesh introspection contracts are consistent across all action types
- pagination fields are standardized
- structured mesh responses are delivered through `structuredContent` and validated against declared `outputSchema`

---

## Atomic Work Items

1. Standardize envelope fields for all `mesh_inspect` actions.
2. Normalize per-item schemas for vertices, edges, faces, normals, UVs, attributes, shape keys, and weights.
3. Return native dict / model payloads from mesh inspection adapters so FastMCP can emit `structuredContent` directly.
4. Add paging and selection-filter tests for every action family.
