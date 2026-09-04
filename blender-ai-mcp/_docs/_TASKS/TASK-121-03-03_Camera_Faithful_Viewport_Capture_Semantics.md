# TASK-121-03-03: Camera-Faithful Viewport Capture Semantics

**Parent:** [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The addon now routes `scene_get_viewport(camera_name=...)` away from the live-user OpenGL viewport path and through a scene-camera render path instead. Unit coverage is in place for the branch split, and the Blender-backed E2E camera-vs-user-perspective regression test passes locally against a live Blender session.

---

## Objective

Ensure `scene_get_viewport(camera_name=...)` captures the named camera view
instead of falling back to the live user viewport perspective.

---

## Business Problem

The current `scene_get_viewport` contract implies that providing `camera_name`
should render from that camera. In practice, the addon first tries the
OpenGL/viewport path, which follows the active 3D View state rather than the
named scene camera.

That breaks:

- camera-faithful visual verification
- deterministic capture bundles
- any vision flow that depends on exact camera placement

---

## Implementation Direction

- when `camera_name` is provided and not `USER_PERSPECTIVE`, do not use the
  live-user OpenGL viewport path as the primary renderer
- prefer a scene-camera-based render path instead
- keep `USER_PERSPECTIVE` behavior unchanged for ad hoc viewport checks
- add Blender-backed E2E coverage for camera-vs-user-perspective behavior

---

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/fixtures/vision_eval/`

---

## Acceptance Criteria

- `scene_get_viewport(camera_name=...)` follows the named camera view
- `scene_get_viewport(camera_name=\"USER_PERSPECTIVE\")` keeps the viewport/user-view behavior
- unit and E2E coverage exist for the split behavior
