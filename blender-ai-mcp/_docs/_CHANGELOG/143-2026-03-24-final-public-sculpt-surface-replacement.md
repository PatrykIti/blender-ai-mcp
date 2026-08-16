# 143 - 2026-03-24: Final public sculpt surface replacement

**Status**: ✅ Completed  
**Type**: Feature / Surface Replacement  
**Task**: TASK-112-04, TASK-112-06

---

## Summary

Completed the public sculpt-surface replacement wave.

The MCP sculpt surface now exposes deterministic region tools instead of the
remaining brush-dependent write tools.

Final public write-side sculpt surface:

- `sculpt_deform_region`
- `sculpt_crease_region`
- `sculpt_smooth_region`
- `sculpt_inflate_region`
- `sculpt_pinch_region`

---

## Changes

- Added `sculpt_crease_region`.
- Removed the remaining brush-dependent sculpt setup tools from the public MCP surface.
- Updated router metadata, docs, and local config examples to the new deterministic sculpt surface.
- Updated compatibility counts for `legacy-manual` / `legacy-flat` first-page catalogs after the sculpt surface shrink.

---

## Files Modified (high level)

- `server/domain/tools/sculpt.py`
- `server/application/tool_handlers/sculpt_handler.py`
- `blender_addon/application/handlers/sculpt.py`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `.mcp.json`
- `.claude/settings.local.json`
- `tests/unit/tools/sculpt/`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

---

## Validation

- `poetry run pytest tests/unit/tools/sculpt/test_sculpt_handler_rpc.py tests/unit/tools/sculpt/test_sculpt_tools.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_search_surface.py -q`
