# 134 - 2026-03-23: Modeling transform RPC result alignment

**Status**: ✅ Completed  
**Type**: Bugfix / Runtime Alignment  
**Task**: TASK-106

---

## Summary

Fixed a server/addon RPC contract mismatch for `modeling_transform_object`.

The addon returned a dict payload for `modeling.transform_object`, while the
server-side modeling handler still expected a plain string. This caused the MCP
tool to fail even though Blender had already applied the transform successfully.

---

## Changes

- Switched the server-side modeling handler to accept the structured dict payload returned by the addon for `modeling.transform_object`.
- Added a focused regression test for the exact RPC response shape returned by the addon.

---

## Files Modified (high level)

- `server/application/tool_handlers/modeling_handler.py`
- `tests/unit/tools/modeling/test_modeling_handler_rpc.py`

---

## Validation

- `poetry run pytest tests/unit/tools/modeling/test_modeling_handler_rpc.py tests/unit/tools/modeling/test_modeling_tools.py -q`
