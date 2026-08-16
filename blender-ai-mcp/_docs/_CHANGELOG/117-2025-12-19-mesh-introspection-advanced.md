# 117 - 2025-12-19: Mesh introspection advanced (normals/weights/attributes/shape keys)

**Status**: ✅ Completed  
**Type**: Feature / Tools / Introspection  
**Task**: TASK-071

---

## Summary

Added advanced mesh introspection tools for loop normals, vertex group weights, attributes, and shape keys with optional deltas.

---

## Changes

- Added addon RPC handlers for loop normals, vertex group weights, attributes, and shape keys (with sparse deltas).
- Added MCP tool wrappers, server handlers, and dispatcher mappings for new mesh introspection tools.
- Added router tool metadata JSON files for the new mesh introspection tools.
- Added unit tests for loop normals, vertex group weights, attributes, and shape key deltas.
- Updated docs (tools summary, mesh tools architecture, MCP server, addon, and task status).

---

## Files Modified (high level)

- Addon:
  - `blender_addon/application/handlers/mesh.py`
  - `blender_addon/__init__.py`
  - `blender_addon/infrastructure/rpc_server.py`
- MCP Server:
  - `server/domain/tools/mesh.py`
  - `server/application/tool_handlers/mesh_handler.py`
  - `server/adapters/mcp/areas/mesh.py`
  - `server/adapters/mcp/dispatcher.py`
- Router metadata:
  - `server/router/infrastructure/tools_metadata/mesh/mesh_get_loop_normals.json`
  - `server/router/infrastructure/tools_metadata/mesh/mesh_get_vertex_group_weights.json`
  - `server/router/infrastructure/tools_metadata/mesh/mesh_get_attributes.json`
  - `server/router/infrastructure/tools_metadata/mesh/mesh_get_shape_keys.json`
- Tests:
  - `tests/unit/tools/mesh/test_get_loop_normals.py`
  - `tests/unit/tools/mesh/test_get_vertex_group_weights.py`
  - `tests/unit/tools/mesh/test_get_attributes.py`
  - `tests/unit/tools/mesh/test_get_shape_keys.py`
- Docs:
  - `README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_ADDON/README.md`
  - `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md`
  - `_docs/_TASKS/TASK-071_Mesh_Introspection_Advanced.md`
  - `_docs/_TASKS/README.md`

---

## Validation

Not run (docs + unit tests only).
