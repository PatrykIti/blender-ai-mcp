# 141 - 2026-03-23: Programmatic sculpt deform-region foundation

**Status**: ✅ Completed  
**Type**: Feature / Sculpt Write Path  
**Task**: TASK-112-01, TASK-112-02

---

## Summary

Implemented the first real programmatic sculpt write path for LLM clients:
`sculpt_deform_region`.

This adds the shared region/falloff engine and replaces public brush-style grab
deformation with a deterministic, geometry-driven tool.

---

## Changes

- Added shared region/falloff/symmetry logic in the addon sculpt handler.
- Added public tool `sculpt_deform_region` through domain, server handler, addon RPC, MCP adapter, dispatcher, and router metadata.
- Replaced public `sculpt_brush_grab` exposure with `sculpt_deform_region` on the sculpt MCP surface.
- Updated docs and local config examples to use the new tool name.
- Added unit and e2e coverage for the new deformation path.

---

## Files Modified (high level)

- `server/domain/tools/sculpt.py`
- `server/application/tool_handlers/sculpt_handler.py`
- `blender_addon/application/handlers/sculpt.py`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `tests/unit/tools/sculpt/`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Validation

- `poetry run pytest tests/unit/tools/sculpt/test_sculpt_handler_rpc.py tests/unit/tools/sculpt/test_sculpt_tools.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py -q`
