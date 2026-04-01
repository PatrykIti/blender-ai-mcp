# 133 - 2026-03-23: Legacy-flat single-page tool catalog

**Status**: ✅ Completed  
**Type**: Compatibility / Platform UX  
**Task**: TASK-105

---

## Summary

Adjusted the `legacy-flat` MCP surface so the current tool catalog fits into a single `tools/list` page.

This is a compatibility workaround for clients that fail to follow `nextCursor` and therefore silently lose later tool families such as `modeling_*`.

---

## Changes

- Increased the default `legacy-flat` component `list_page_size` from `100` to `250`.
- Added a low-level MCP pagination regression test that verifies the first `tools/list` page now contains the full current legacy catalog and returns no `nextCursor`.
- Documented the workaround as a compatibility measure rather than a change to the MCP pagination contract itself.

---

## Files Modified (high level)

- `server/adapters/mcp/surfaces.py`
- `tests/unit/adapters/mcp/test_pagination_policy.py`
- `tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

---

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_pagination_policy.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py -q`
