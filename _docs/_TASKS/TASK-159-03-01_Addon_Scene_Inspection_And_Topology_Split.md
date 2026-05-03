# TASK-159-03-01: Addon Scene Inspection And Topology Split

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract inspection, hierarchy, bbox/origin, and topology helpers from addon
`SceneHandler` while preserving Blender-owned truth reads.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely new helper module such as `blender_addon/application/handlers/scene_inspection_mixin.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`

## Current Code Anchors

- `SceneHandler.inspect_object(...)`
- `SceneHandler.snapshot_state(...)`
- `SceneHandler.get_hierarchy(...)`
- `SceneHandler.get_bounding_box(...)`
- `SceneHandler.get_origin_info(...)`
- `SceneHandler.inspect_mesh_topology(...)`

## Planned Code Shape

```python
class SceneHandler(SceneInspectionMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- keep Blender state reads on the main-thread-safe addon path
- preserve current topology payload shapes and bbox/origin conventions
- do not move truth reads into server-side services during this leaf

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/test_handler_rpc_alignment.py -q`

## Docs To Update

- inherit parent docs closeout unless addon inspection ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- inspection/topology helpers are no longer inline with unrelated viewport or
  measure/assert code
- Blender truth-read payloads stay unchanged
- RPC alignment tests still pass for the extracted inspection methods

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
