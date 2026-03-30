# 166 - 2026-03-30: User-view viewport capture controls

**Status**: ✅ Completed  
**Type**: Viewport Capture / Guided UX  
**Task**: TASK-121-03-04

---

## Summary

Formalized the bounded user-view capture path for `scene_get_viewport(...)`.

The tool already supported:

- `view_name`
- `orbit_horizontal`
- `orbit_vertical`
- `zoom_factor`
- `persist_view`

on the `USER_PERSPECTIVE` path, with branch coverage and Blender-backed tests.
This change closes the task formally and updates the public docs so the
bounded user-view adjustment semantics are part of the documented MCP surface.
