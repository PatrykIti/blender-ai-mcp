# TASK-159-03-04-02: Addon Scene Mode And Visibility Utility Split

**Parent:** [TASK-159-03-04](./TASK-159-03-04_Addon_Scene_Creation_Visibility_And_Metadata_Utilities.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate mode-switch, rename, visibility, and isolation helpers into one
focused addon utility leaf.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as `blender_addon/application/handlers/scene_utility_mixin.py`
- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_hide_object.py`
- `tests/unit/tools/scene/test_show_all_objects.py`
- `tests/unit/tools/scene/test_rename_object.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Current Code Anchors

- `SceneHandler.set_mode(...)`
- `SceneHandler.rename_object(...)`
- `SceneHandler.hide_object(...)`
- `SceneHandler.show_all_objects(...)`
- `SceneHandler.isolate_object(...)`

## Planned Code Shape

```python
class SceneHandler(SceneModeVisibilityUtilityMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve current object-mode assumptions and validation errors for `set_mode(...)`
- preserve visibility/isolation payloads and side effects unchanged

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_hide_object.py`
- `tests/unit/tools/scene/test_show_all_objects.py`
- `tests/unit/tools/scene/test_rename_object.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_hide_object.py tests/unit/tools/scene/test_show_all_objects.py tests/unit/tools/scene/test_rename_object.py tests/unit/tools/scene/test_isolate_object.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_utility_workflow.py -q`

## Docs To Update

- inherit parent docs closeout unless mode/visibility ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- mode-switch, rename, visibility, and isolation helpers have a focused home
- object-mode assumptions and validation errors remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
