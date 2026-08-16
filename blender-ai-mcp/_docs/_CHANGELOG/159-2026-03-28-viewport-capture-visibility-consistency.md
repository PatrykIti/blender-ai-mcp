# 159 - 2026-03-28: Viewport capture visibility consistency

**Status**: ✅ Completed  
**Type**: Bugfix / LLM UX Hardening  
**Task**: TASK-121-03-05

---

## Summary

Aligned viewport capture semantics so staged screenshot flows no longer need a
render-visibility reset workaround before every named-camera capture.

The fix covered two related issues:

- `scene_get_viewport(camera_name="USER_PERSPECTIVE")` could drift away from
  the live user viewport because the old path could create/frame a temporary
  camera instead of simply capturing the active 3D view
- scene visibility helpers could leave viewport visibility and render
  visibility out of sync, which meant named-camera captures did not match what
  the user saw in the viewport

---

## Changes

- Kept the primary `USER_PERSPECTIVE` path on the live viewport/OpenGL capture
  flow.
- Limited temporary-camera mirroring to the fallback render path only.
- Made `scene_isolate_object(...)` hide non-target objects in both viewport and
  render.
- Made `scene_hide_object(..., hide=False, ...)` restore render visibility as
  well.
- Improved `scene_show_all_objects(include_render=True)` status reporting so the
  returned message reflects restored render visibility counts.
- Updated public docs/prompts to explain that named-camera capture follows
  render visibility and that the visibility helpers are now aligned with that
  behavior.

---

## Files Modified (high level)

- `blender_addon/application/handlers/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/TOOLS/SCENE_TOOLS_ARCHITECTURE.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `_docs/_TASKS/TASK-121-03_Before_After_Capture_And_Macro_Integration.md`
- `_docs/_TASKS/TASK-121-03-05_Render_Visibility_Consistency_For_Viewport_Capture.md`
- `tests/unit/tools/scene/test_hide_object.py`
- `tests/unit/tools/scene/test_show_all_objects.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/tools/scene/test_viewport_control.py`

---

## Validation

- `poetry run pytest -q tests/unit/tools/scene/test_hide_object.py tests/unit/tools/scene/test_show_all_objects.py tests/unit/tools/scene/test_isolate_object.py tests/unit/tools/scene/test_viewport_control.py tests/unit/tools/scene/test_mcp_viewport_output.py`
- `poetry run ruff check blender_addon/application/handlers/scene.py server/adapters/mcp/areas/scene.py tests/unit/tools/scene/test_hide_object.py tests/unit/tools/scene/test_show_all_objects.py tests/unit/tools/scene/test_isolate_object.py tests/unit/tools/scene/test_viewport_control.py`
