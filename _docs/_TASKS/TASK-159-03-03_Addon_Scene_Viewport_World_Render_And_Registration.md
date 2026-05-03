# TASK-159-03-03: Addon Scene Viewport World Render And Registration

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract viewport, camera utility, and world/render/color-management helpers from
addon `SceneHandler` and prove that addon registration plus server roundtrip
wiring remain unchanged.

MCP output-mode formatting and task-mode background bridging are tracked on the
server-side scene facade under
[TASK-159-02-06](./TASK-159-02-06_Scene_Viewport_Background_Bridge_And_Output_Surface.md).
This leaf owns the Blender/runtime viewport behavior itself.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper modules such as:
  - `blender_addon/application/handlers/scene_viewport_mixin.py`
  - `blender_addon/application/handlers/scene_world_render_mixin.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/addon/test_addon_registration.py`
- `tests/unit/tools/scene/test_scene_configure_handler.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Current Code Anchors

- `SceneHandler.get_viewport(...)`
- `SceneHandler.get_view_diagnostics(...)`
- `SceneHandler.camera_orbit(...)`
- `SceneHandler.camera_focus(...)`
- `SceneHandler.inspect_color_management(...)`
- `SceneHandler.inspect_world(...)`
- `SceneHandler.configure_color_management(...)`
- `SceneHandler.configure_world(...)`
- `SceneHandler.inspect_render_settings(...)`
- `SceneHandler.configure_render_settings(...)`
- `SceneHandler.get_view_state(...)`
- `SceneHandler.restore_view_state(...)`
- `SceneHandler.set_standard_view(...)`
- addon `register()` scene handler wiring

## Planned Code Shape

```python
class SceneHandler(SceneViewportMixin, SceneWorldRenderMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve main-thread-safe viewport capture, camera utility behavior, and
  temporary view restoration
- preserve `USER_PERSPECTIVE` vs named-camera behavior and the current
  restore-default-view semantics after temporary user-view adjustments
- preserve current world/render/color-management payloads, including
  `node_graph_handoff` boundaries
- keep addon registration and RPC background-handler wiring unchanged

## Tests To Add/Update

- `tests/unit/addon/test_addon_registration.py`
- `tests/unit/tools/scene/test_scene_configure_handler.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/addon/test_addon_registration.py tests/unit/tools/scene/test_scene_configure_handler.py tests/unit/tools/scene/test_camera_orbit.py tests/unit/tools/scene/test_camera_focus.py tests/unit/tools/scene/test_viewport_control.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_get_viewport.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py tests/e2e/tools/scene/test_scene_configure_roundtrip.py tests/e2e/tools/scene/test_camera_orbit.py tests/e2e/tools/scene/test_camera_focus.py tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`

## Docs To Update

- `_docs/_ADDON/README.md` only if the internal addon owner map is documented

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- viewport/camera and world/render/color-management helpers are isolated from
  unrelated scene concerns
- addon registration continues to expose the same scene RPC handlers
- roundtrip world/render/color-management plus Blender-backed viewport
  regressions for `USER_PERSPECTIVE` restore and named-camera capture stay green

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
