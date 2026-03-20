# 119 - 2025-12-19: Rig, curve, and lattice introspection

**Status**: ✅ Completed  
**Type**: Feature / Tools / Introspection  
**Task**: TASK-073

---

## Summary

Added curve, lattice, and armature introspection tools for full reconstruction of splines, control points, and bone hierarchies.

---

## Changes

- Added addon RPC handlers for curve spline dumps, lattice control points, and armature bone/pose data.
- Added MCP tool wrappers, server handlers, and dispatcher mappings for new introspection tools.
- Added router tool metadata JSON files.
- Added unit tests for curve, lattice, and armature introspection.
- Updated docs (addon, MCP server, tools summaries, and task status).

---

## Files Modified (high level)

- Addon:
  - `blender_addon/application/handlers/curve.py`
  - `blender_addon/application/handlers/lattice.py`
  - `blender_addon/application/handlers/armature.py`
  - `blender_addon/__init__.py`
  - `blender_addon/infrastructure/rpc_server.py`
- MCP Server:
  - `server/domain/tools/curve.py`
  - `server/domain/tools/lattice.py`
  - `server/domain/tools/armature.py`
  - `server/application/tool_handlers/curve_handler.py`
  - `server/application/tool_handlers/lattice_handler.py`
  - `server/application/tool_handlers/armature_handler.py`
  - `server/adapters/mcp/areas/curve.py`
  - `server/adapters/mcp/areas/lattice.py`
  - `server/adapters/mcp/areas/armature.py`
  - `server/adapters/mcp/dispatcher.py`
- Router metadata:
  - `server/router/infrastructure/tools_metadata/curve/curve_get_data.json`
  - `server/router/infrastructure/tools_metadata/lattice/lattice_get_points.json`
  - `server/router/infrastructure/tools_metadata/armature/armature_get_data.json`
- Tests:
  - `tests/unit/tools/curve/test_get_data.py`
  - `tests/unit/tools/lattice/test_get_points.py`
  - `tests/unit/tools/armature/test_get_data.py`
- Docs:
  - `README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_ADDON/README.md`
  - `_docs/TOOLS/CURVE_TOOLS_ARCHITECTURE.md`
  - `_docs/TOOLS/LATTICE_TOOLS_ARCHITECTURE.md`
  - `_docs/_TASKS/TASK-073_Rig_Curve_Lattice_Introspection.md`
  - `_docs/_TASKS/README.md`

---

## Validation

`PYTHONPATH=. poetry run pytest`
