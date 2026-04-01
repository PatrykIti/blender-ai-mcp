# 125 - 2026-03-23: Task-capable surface instructions

**Status**: ✅ Completed  
**Type**: UX / Documentation  
**Task**: task-mode usability follow-up

---

## Summary

Made task-mode usage explicit at the surface-instructions layer for task-capable MCP profiles, so models can discover that background execution exists without reverse-engineering it from the repo docs.

---

## Changes

- Added task-mode guidance to `llm-guided` surface instructions.
- Added task-mode guidance to `internal-debug` surface instructions.
- Expanded `code-mode-pilot` instructions to note its task-capable status and scope expectations.
- Updated README and MCP server docs so the same task-capable profile guidance is visible to maintainers.

---

## Files Modified (high level)

- `server/adapters/mcp/surfaces.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `tests/unit/adapters/mcp/test_server_factory.py`

---

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_server_factory.py -q`
