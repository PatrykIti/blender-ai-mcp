# 120 - 2025-12-19: Mesh inspect mega tool

**Status**: ✅ Completed  
**Type**: Feature / Mega Tools / Introspection  
**Task**: TASK-074

---

## Summary

Added the `mesh_inspect` mega tool to consolidate mesh introspection payloads and introduced a lightweight summary mode.
Single-action introspection wrappers covered by mega tools were internalized to reduce MCP tool surface area.

---

## Changes

- Added `mesh_inspect` mega tool with action routing and summary payload.
- Converted `mesh_get_*` introspection wrappers to internal functions (mega-tool only).
- Removed MCP wrappers for `scene_get_constraints` and `modeling_get_modifier_data` (handled via `scene_inspect`).
- Added router metadata for `mesh_inspect`.
- Updated metadata alignment tests to allow dispatcher-only tools.
- Added unit tests for `mesh_inspect` routing.
- Updated docs (mega tools counts, internal tool notes, task status).

---

## Files Modified (high level)

- MCP Server:
  - `server/adapters/mcp/areas/mesh.py`
  - `server/adapters/mcp/areas/scene.py`
  - `server/adapters/mcp/areas/modeling.py`
  - `server/router/infrastructure/tools_metadata/mesh/mesh_inspect.json`
- Tests:
  - `tests/unit/tools/mesh/test_mesh_inspect_mega.py`
  - `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- Docs:
  - `README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md`
  - `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md`
  - `_docs/TOOLS/SCENE_TOOLS_ARCHITECTURE.md`
  - `_docs/TOOLS/MODELING_TOOLS_ARCHITECTURE.md`
  - `_docs/_TASKS/TASK-074_Mesh_Inspect_Mega_Tool.md`
  - `_docs/_TASKS/README.md`

---

## Validation

`PYTHONPATH=. poetry run pytest`
