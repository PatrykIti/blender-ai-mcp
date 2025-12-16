# 114 - 2025-12-16: Addon auto-undo push for granular `system_undo`

**Status**: ✅ Completed  
**Type**: Bug Fix / UX / Safety  
**Task**: -

---

## Summary

Improved undo granularity for MCP-driven modeling sessions. Previously, Blender could group multiple tool calls into a single undo step, so `system_undo(steps=1)` could revert minutes of work.

The addon now best-effort inserts an undo boundary after successful **mutating** RPC commands, making undo behavior much closer to “one tool call = one undo step”.

---

## Changes

- Addon RPC server pushes an undo step after successful mutating commands (best-effort).
- Read-only / inspection / export / bake / selection-type calls are excluded to avoid undo spam.
- Added an opt-out switch: set `BLENDER_AI_MCP_AUTO_UNDO_PUSH=0` to disable automatic undo boundaries.

---

## Files Modified (high level)

- Addon:
  - `blender_addon/infrastructure/rpc_server.py`

---

## Validation

```bash
poetry run pytest tests/unit/ -q
```

