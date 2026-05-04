# TASK-159-03-05: Addon Scene World, Render, And Color Management Split

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate world/render/color-management helpers from addon `SceneHandler` while
preserving RPC payloads, `node_graph_handoff` boundaries, and read/apply/read
roundtrip behavior for scene appearance state.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as
  `blender_addon/application/handlers/scene_world_render_mixin.py`
- `server/application/tool_handlers/scene_handler.py`
- `tests/unit/tools/scene/test_scene_configure_handler.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`

## Current Code Anchors

- `SceneHandler.inspect_render_settings(...)`
- `SceneHandler.inspect_color_management(...)`
- `SceneHandler.inspect_world(...)`
- `SceneHandler.configure_render_settings(...)`
- `SceneHandler.configure_color_management(...)`
- `SceneHandler.configure_world(...)`

## Planned Code Shape

```python
class SceneHandler(SceneWorldRenderMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve current render/color-management/world payloads and reject-unsupported
  behavior, including the existing `node_graph_handoff` boundary
- preserve read/apply/read roundtrip semantics for grouped configure flows so
  scene appearance state remains reproducible from structured payloads
- keep server-addon RPC method names and payload alignment unchanged while the
  Blender-owned helpers move behind a mixin seam

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_configure_handler.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_configure_handler.py tests/unit/tools/test_handler_rpc_alignment.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_configure_roundtrip.py -q`

## Docs To Update

- inherit parent docs closeout unless addon scene-appearance ownership wording
  changes in `_docs/_ADDON/README.md`

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- world/render/color-management helpers no longer share one edit zone with
  viewport/camera or unrelated utility logic inside addon `SceneHandler`
- RPC method names, payloads, and `node_graph_handoff` boundaries remain stable
- Blender-backed configure roundtrip still proves the same read/apply/read
  behavior for render, color-management, and world settings

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
- treat this as the scene-appearance companion to `TASK-159-03-03` so viewport
  runtime extraction does not also absorb grouped render/world work
