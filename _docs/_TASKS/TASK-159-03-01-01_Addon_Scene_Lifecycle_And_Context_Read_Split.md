# TASK-159-03-01-01: Addon Scene Lifecycle And Context Read Split

**Parent:** [TASK-159-03-01](./TASK-159-03-01_Addon_Scene_Inspection_And_Topology_Split.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate early object lifecycle helpers plus mode/selection/context reads into
one focused addon leaf.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as `blender_addon/application/handlers/scene_lifecycle_context_mixin.py`
- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`

## Current Code Anchors

- `SceneHandler.list_objects(...)`
- `SceneHandler.delete_object(...)`
- `SceneHandler.clean_scene(...)`
- `SceneHandler.duplicate_object(...)`
- `SceneHandler.set_active_object(...)`
- `SceneHandler.get_mode(...)`
- `SceneHandler.list_selection(...)`

## Planned Code Shape

```python
class SceneHandler(SceneLifecycleContextMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve object-mode safety, lifecycle payloads, and current mode/selection
  result envelopes
- keep Blender-owned lifecycle truth helpers on the main-thread-safe addon path

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_get_mode_handler.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_clean_scene.py -q`

## Docs To Update

- inherit parent docs closeout unless lifecycle/context ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- lifecycle helpers plus mode/selection/context reads have a focused home
  outside the monolithic handler
- lifecycle/context payloads and Blender safety semantics remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
