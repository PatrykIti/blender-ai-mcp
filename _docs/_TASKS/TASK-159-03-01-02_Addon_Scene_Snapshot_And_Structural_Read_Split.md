# TASK-159-03-01-02: Addon Scene Snapshot And Structural Read Split

**Parent:** [TASK-159-03-01](./TASK-159-03-01_Addon_Scene_Inspection_And_Topology_Split.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate snapshot and structural-read helpers into one focused addon leaf.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as `blender_addon/application/handlers/scene_structural_read_mixin.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Current Code Anchors

- `SceneHandler.snapshot_state(...)`
- `SceneHandler.get_hierarchy(...)`
- `SceneHandler.get_bounding_box(...)`
- `SceneHandler.get_origin_info(...)`

## Planned Code Shape

```python
class SceneHandler(SceneStructuralReadMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve snapshot, hierarchy, bbox, and origin payload conventions
- keep structural reads on the same Blender-owned truth path and safety model

## Tests To Add/Update

- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_snapshot_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless structural-read ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- snapshot and structural-read helpers have a focused home outside the
  monolithic handler
- snapshot, hierarchy, bbox, and origin contracts remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
