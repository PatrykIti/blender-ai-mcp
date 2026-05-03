# TASK-159-03-01: Addon Scene Context, Lifecycle, Inspection, And Topology Split

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract scene lifecycle/context, snapshot/structural-read, inspection, and
topology helpers from addon `SceneHandler` while preserving Blender-owned truth
reads.

This leaf owns the truth-read surface plus the early object-lifecycle helpers
that currently sit next to it in `SceneHandler`. Creation, visibility, and
custom-property utilities move under
[TASK-159-03-04](./TASK-159-03-04_Addon_Scene_Creation_Visibility_And_Metadata_Utilities.md).

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely new helper module such as `blender_addon/application/handlers/scene_inspection_mixin.py`
- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Current Code Anchors

- `SceneHandler.list_objects(...)`
- `SceneHandler.delete_object(...)`
- `SceneHandler.clean_scene(...)`
- `SceneHandler.duplicate_object(...)`
- `SceneHandler.set_active_object(...)`
- `SceneHandler.get_mode(...)`
- `SceneHandler.list_selection(...)`
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

- keep Blender state reads and object-lifecycle truth helpers on the
  main-thread-safe addon path
- preserve current topology payload shapes plus snapshot/hierarchy/bbox/origin
  conventions
- preserve current list/clean/duplicate/set-active/get-mode/list-selection
  semantics and result envelopes
- do not move truth reads into server-side services during this leaf

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_get_mode_handler.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_clean_scene.py tests/e2e/tools/scene/test_snapshot_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless addon inspection ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- inspection/topology helpers are no longer inline with unrelated viewport or
  measure/assert code
- lifecycle/context helpers no longer share one anonymous edit zone with later
  create/visibility/viewport code
- Blender truth-read payloads stay unchanged for list/clean/duplicate/mode,
  inspect, snapshot, hierarchy, bbox/origin, and topology paths
- RPC alignment tests still pass for the extracted lifecycle/context/inspection
  methods

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
