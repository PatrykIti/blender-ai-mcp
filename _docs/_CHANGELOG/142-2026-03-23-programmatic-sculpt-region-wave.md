# 142 - 2026-03-23: Programmatic sculpt region wave

**Status**: ✅ Completed  
**Type**: Feature / Sculpt Write Path  
**Task**: TASK-112-03, TASK-112-05

---

## Summary

Expanded the first-wave deterministic sculpt surface with:

- `sculpt_smooth_region`
- `sculpt_inflate_region`
- `sculpt_pinch_region`

These tools join `sculpt_deform_region` to form the first real programmatic
regional sculpt family for LLM clients.

---

## Changes

- Added three new region-based sculpt tools across domain, server handler, addon RPC, MCP adapter, dispatcher, router metadata, and docs.
- Removed the public sculpt-surface exposure of `sculpt_brush_smooth`, `sculpt_brush_inflate`, and `sculpt_brush_pinch`.
- Updated local config examples and public tool inventories to the new region-tool names.
- Added unit coverage plus Blender-backed e2e smoke tests for the first-wave region tools.

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

- `poetry run pytest tests/unit/tools/sculpt/test_sculpt_handler_rpc.py tests/unit/tools/sculpt/test_sculpt_tools.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py tests/unit/adapters/mcp/test_server_factory.py -q`
