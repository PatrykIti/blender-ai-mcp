# TASK-159-02-02-03: Scene Inspect Action Matrix And Contract Slices

**Parent:** [TASK-159-02-02](./TASK-159-02-02_Scene_Context_Inspect_Snapshot_And_Structural_Read_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate the full `scene_inspect(...)` action matrix into one focused leaf so
the object/topology/material/modifier/constraint/modifier_data/render/color/
world branches keep one explicit owner.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely helper module such as `server/adapters/mcp/areas/scene_inspect.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_inspect_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`

## Current Code Anchors

- `scene_inspect(...)`
- `_scene_inspect_object(...)`
- `_scene_inspect_mesh_topology(...)`
- `_scene_inspect_material_slots(...)`
- `_scene_inspect_modifiers(...)`
- `_scene_get_constraints(...)`
- `_scene_inspect_modifier_data(...)`
- `_scene_inspect_render_settings(...)`
- `_scene_inspect_color_management(...)`
- `_scene_inspect_world(...)`

## Planned Code Shape

```python
from .scene_inspect import execute_scene_inspect
```

## Runtime / Security Contract Notes

- preserve the current typed inspect action vocabulary and response envelopes
- keep object, topology, materials, modifiers, constraints, modifier_data,
  render, color_management, and world branches on the same inspect owner seam

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_inspect_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_inspect_mega.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/scene/test_scene_inspect_modifiers.py tests/unit/tools/scene/test_get_constraints.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/e2e/tools/scene/test_scene_inspect_material_slots.py -q`

## Docs To Update

- inherit parent docs closeout unless inspect-action ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- the full `scene_inspect(...)` action matrix has one focused home outside the
  monolith
- typed inspect contracts remain unchanged across object/topology/material/
  modifier/constraint/modifier_data/render/color_management/world branches

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
