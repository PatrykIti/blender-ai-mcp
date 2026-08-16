# 139 - 2026-03-23: Modeling modifier RPC alignment and sculpt grab boundary

**Status**: ✅ Completed  
**Type**: Bugfix / UX Clarification  
**Task**: TASK-111

---

## Summary

Fixed a real RPC contract bug for `modeling_add_modifier` and clarified the
surface semantics of `sculpt_brush_grab`.

`modeling_add_modifier` now accepts the structured dict payload returned by the
addon, while `sculpt_brush_grab` now clearly states that it only configures the
Grab brush and does not execute a geometry-changing stroke by itself.

---

## Changes

- Switched the server-side modeling handler to accept structured dict results from `modeling.add_modifier`.
- Reworded `sculpt_brush_grab` in the addon, MCP adapter, router metadata, and docs so it no longer implies that geometry was modified.
- Added regression tests for modifier RPC result alignment and the grab-brush semantic boundary.

---

## Files Modified (high level)

- `server/application/tool_handlers/modeling_handler.py`
- `blender_addon/application/handlers/sculpt.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/router/infrastructure/tools_metadata/sculpt/sculpt_brush_grab.json`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `tests/unit/tools/modeling/test_modeling_handler_rpc.py`
- `tests/unit/tools/sculpt/test_sculpt_tools.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

---

## Validation

- `poetry run pytest tests/unit/tools/modeling/test_modeling_handler_rpc.py tests/unit/tools/modeling/test_modeling_tools.py tests/unit/tools/sculpt/test_sculpt_tools.py -q`
