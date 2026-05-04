# TASK-159-03-01-03: Addon Scene Inspection Action Matrix And Topology Split

**Parent:** [TASK-159-03-01](./TASK-159-03-01_Addon_Scene_Inspection_And_Topology_Split.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate the inspection action matrix plus topology helpers into one focused
addon truth-read leaf.

## Repository Touchpoints

- `blender_addon/application/handlers/scene.py`
- likely helper module such as `blender_addon/application/handlers/scene_inspection_mixin.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`

## Current Code Anchors

- `SceneHandler.inspect_object(...)`
- `SceneHandler.inspect_material_slots(...)`
- `SceneHandler.inspect_modifiers(...)`
- `SceneHandler.get_constraints(...)`
- `SceneHandler.inspect_mesh_topology(...)`

## Planned Code Shape

```python
class SceneHandler(SceneInspectionMixin, ...):
    pass
```

## Runtime / Security Contract Notes

- preserve the same Blender-owned truth path for object/material/modifier/
  constraint/topology inspection
- keep typed inspection payloads and evaluated-mesh safety unchanged

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_scene_get_mode_handler.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_get_mode_handler.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_inspect_modifiers.py tests/unit/tools/scene/test_get_constraints.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/test_handler_rpc_alignment.py tests/e2e/tools/scene/test_scene_inspect_material_slots.py -q`

## Docs To Update

- inherit parent docs closeout unless inspection/topology ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- inspection action-matrix helpers plus topology have a focused home outside
  the monolithic handler
- object/material/modifier/constraint/topology payloads remain unchanged

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
