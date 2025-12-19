# 116 - 2025-12-19: Mesh topology introspection tools (edges/faces/UVs)

**Status**: ✅ Completed  
**Type**: Feature / Tools / Introspection  
**Task**: TASK-070

---

## Summary

Added mesh topology introspection tools to retrieve edges, faces, and UV loop data for 1:1 reconstruction.

---

## Changes

- Added `mesh_get_edge_data`, `mesh_get_face_data`, and `mesh_get_uv_data` to addon handlers and RPC registration.
- Added MCP tool wrappers, server handlers, and dispatcher mappings for new tools.
- Added router tool metadata JSON files for the new mesh introspection tools.
- Added unit tests for edge/face/UV introspection outputs.
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
  - `server/router/infrastructure/tools_metadata/mesh/mesh_get_edge_data.json`
  - `server/router/infrastructure/tools_metadata/mesh/mesh_get_face_data.json`
  - `server/router/infrastructure/tools_metadata/mesh/mesh_get_uv_data.json`
- Tests:
  - `tests/unit/tools/mesh/test_mesh_topology_introspection.py`
- Docs:
  - `README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_ADDON/README.md`
  - `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md`
  - `_docs/_TASKS/TASK-070_Mesh_Topology_Introspection_Extensions.md`
  - `_docs/_TASKS/README.md`

---

## Validation

Not run (docs + unit tests only).
