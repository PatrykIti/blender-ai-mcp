# TASK-159-03-01: Addon Scene Context, Lifecycle, Inspection, And Topology Split

**Parent:** [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split the addon truth-read branch into focused lifecycle/context, structural
read, and inspection/topology leaves so the Blender owner path stays
execution-ready under the leaf-size rule.

This subtask still owns the same truth-read surface plus the early
object-lifecycle helpers that currently sit next to it in `SceneHandler`.
Creation, visibility, and custom-property utilities move under
[TASK-159-03-04](./TASK-159-03-04_Addon_Scene_Creation_Visibility_And_Metadata_Utilities.md).

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely new helper modules such as:
  - `blender_addon/application/handlers/scene_lifecycle_context_mixin.py`
  - `blender_addon/application/handlers/scene_structural_read_mixin.py`
  - `blender_addon/application/handlers/scene_inspection_mixin.py`
- `tests/unit/tools/scene/test_scene_mode.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`
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
- `SceneHandler.inspect_material_slots(...)`
- `SceneHandler.inspect_modifiers(...)`
- `SceneHandler.get_constraints(...)`
- `SceneHandler.snapshot_state(...)`
- `SceneHandler.get_hierarchy(...)`
- `SceneHandler.get_bounding_box(...)`
- `SceneHandler.get_origin_info(...)`
- `SceneHandler.inspect_mesh_topology(...)`

## Planned Code Shape

```python
class SceneHandler(
    SceneLifecycleContextMixin,
    SceneStructuralReadMixin,
    SceneInspectionMixin,
    ...,
):
    pass
```

## Implementation Notes

- Keep lifecycle/context helpers separate from structural-read helpers even if
  they land in adjacent addon mixins; they have different validation and RPC
  coupling.
- Keep the inspection action matrix plus topology together only where the same
  Blender-owned truth helpers already share mesh/material/constraint state.
- Leave creation/visibility/custom-property utilities on `TASK-159-03-04` and
  world/render/color-management on `TASK-159-03-05`; do not let this branch
  absorb those responsibilities again.
- Preserve Blender main-thread and evaluated-mesh safety patterns across every
  child leaf.

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-159-03-01-01](./TASK-159-03-01-01_Addon_Scene_Lifecycle_And_Context_Read_Split.md) | Separate early object lifecycle helpers plus mode/selection/context reads into one focused addon leaf |
| 2 | [TASK-159-03-01-02](./TASK-159-03-01-02_Addon_Scene_Snapshot_And_Structural_Read_Split.md) | Separate snapshot, hierarchy, bbox, and origin helpers into one structural-read addon leaf |
| 3 | [TASK-159-03-01-03](./TASK-159-03-01-03_Addon_Scene_Inspection_Action_Matrix_And_Topology_Split.md) | Separate the inspection action matrix plus topology helpers into one focused truth-read addon leaf |

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
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_get_mode_handler.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_inspect_modifiers.py tests/unit/tools/scene/test_get_constraints.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_inspect_material_slots.py tests/e2e/tools/scene/test_scene_clean_scene.py tests/e2e/tools/scene/test_snapshot_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless addon inspection ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- this branch is decomposed into focused lifecycle/context, structural-read,
  and inspection/topology leaves instead of one oversized truth-read pass
- Blender truth-read payloads stay unchanged for list/clean/duplicate/mode,
  inspect, material-slot, modifier, constraint, snapshot, hierarchy,
  bbox/origin, and topology paths across the child leaves
- RPC alignment tests still pass for the extracted lifecycle/context,
  structural-read, and inspection methods

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
- execute this branch through the focused leaves below instead of landing all
  truth-read work in one oversized pass
