# TASK-121-03-05: Render-Visibility Consistency for Viewport Capture

**Parent:** [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_get_viewport(camera_name="USER_PERSPECTIVE")`
now keeps the live user-view semantics instead of reframing the scene through a
temporary camera on the primary path, and the scene visibility helpers now stay
consistent with named-camera capture by aligning viewport and render visibility.

---

## Objective

Remove the visibility mismatch between live-viewport checks and named-camera
viewport capture so stage-based screenshot flows do not need reset-heavy
workarounds.

---

## Problem

Two related inconsistencies were exposed during real capture staging:

- `scene_get_viewport(camera_name="USER_PERSPECTIVE")` could drift away from
  the live user view because the old path could create and frame a temporary
  camera instead of simply capturing the active 3D viewport
- `scene_isolate_object(...)` and `scene_hide_object(...)` primarily changed
  viewport visibility, while named-camera capture follows render visibility

That produced a bad practical loop:

- the viewport looked correct to the user
- the named camera still rendered hidden/non-hidden objects from a different
  visibility state
- the model had to use `scene_show_all_objects(include_render=True)` before
  every stage as a workaround

---

## Solution

- keep `USER_PERSPECTIVE` on the live 3D viewport/OpenGL path whenever that
  path is available
- only mirror the active user view into a temporary camera on the fallback
  render path
- make `scene_isolate_object(...)` hide non-target objects in both viewport and
  render
- make `scene_hide_object(..., hide=False, ...)` restore render visibility too
- clarify the public docs so LLMs know that named-camera capture follows render
  visibility and that visibility helpers are now aligned with that behavior

---

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/TOOLS/SCENE_TOOLS_ARCHITECTURE.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `tests/unit/tools/scene/`

---

## Acceptance Criteria

- `scene_get_viewport(camera_name="USER_PERSPECTIVE")` matches the live user
  viewport on the primary path
- named-camera capture respects the same intended isolated object set without
  requiring a reset workaround before every stage
- public docs explain the visibility semantics clearly enough for LLM-driven
  capture flows
