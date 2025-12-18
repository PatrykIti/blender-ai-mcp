# 115 - 2025-12-16: Fix unawaited `Context.info()` warnings in MCP tool adapters

**Status**: ✅ Completed  
**Type**: Bug Fix / Logging / DX  
**Task**: -

---

## Summary

Fixed `RuntimeWarning: coroutine 'Context.info' was never awaited` emitted by the MCP server when synchronous tool handlers attempted to call `ctx.info(...)`.

Synchronous MCP tools now use a safe bridge that schedules `ctx.info()` correctly without breaking tool execution.

---

## Changes

- Added `ctx_info(ctx, message)` helper to safely call `ctx.info()` from sync code (best-effort scheduling / thread bridging).
- Updated MCP tool adapter areas to use `ctx_info(...)` instead of calling `ctx.info(...)` directly.

---

## Files Modified (high level)

- MCP:
  - `server/adapters/mcp/context_utils.py` *(new)*
  - `server/adapters/mcp/areas/system.py`
  - `server/adapters/mcp/areas/scene.py`
  - `server/adapters/mcp/areas/collection.py`
  - `server/adapters/mcp/areas/material.py`
  - `server/adapters/mcp/areas/mesh.py`
  - `server/adapters/mcp/areas/uv.py`
  - `server/adapters/mcp/areas/router.py`
  - `server/adapters/mcp/areas/extraction.py`

---

## Validation

```bash
poetry run pytest tests/unit/ -q
```

