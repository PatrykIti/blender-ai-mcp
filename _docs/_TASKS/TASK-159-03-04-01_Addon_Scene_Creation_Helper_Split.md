# TASK-159-03-04-01: Addon Scene Creation Helper Split

**Parent:** [TASK-159-03-04](./TASK-159-03-04_Addon_Scene_Creation_Visibility_And_Metadata_Utilities.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate light/camera/empty creation helpers into one focused addon utility
leaf.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as `blender_addon/application/handlers/scene_utility_mixin.py`
- `tests/unit/tools/scene/test_scene_construction.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Current Code Anchors

- `SceneHandler.create_light(...)`
- `SceneHandler.create_camera(...)`
- `SceneHandler.create_empty(...)`

## Planned Code Shape

```python
class SceneHandler(SceneCreationUtilityMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve current creation helper payloads and default handling for
  light/camera/empty operations

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_construction.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_construction.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/e2e/tools/scene/test_scene_utility_workflow.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`

## Docs To Update

- inherit parent docs closeout unless creation-helper ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- creation helpers have a focused home outside the broad utility branch
- current creation payloads and defaults remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
