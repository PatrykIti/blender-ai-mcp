# 136 - 2026-03-23: Scene camera parameter UX clarification

**Status**: ✅ Completed  
**Type**: Docs / LLM UX Hardening  
**Task**: TASK-109

---

## Summary

Clarified the public parameter naming around the scene camera helpers so LLM
clients are less likely to confuse:

- `scene_camera_focus(object_name=...)`
- `scene_camera_orbit(target_object=... | target_point=...)`
- `scene_get_viewport(focus_target=...)`

---

## Changes

- Added an explicit warning to the `scene_camera_focus` MCP tool description.
- Added the missing `scene_camera_orbit` and `scene_camera_focus` rows to the public MCP docs and tool inventory.
- Added a parameter-map reminder to the manual prompt docs.
- Added regression coverage against the real `tools/list` description returned by the server.

---

## Files Modified (high level)

- `server/adapters/mcp/areas/scene.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py`

---

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py -q`
