# 310. TASK-159 addon scene inspection mixin

Date: 2026-05-04

## Summary

- completed `TASK-159-03-01-03` by splitting the addon inspection/topology
  cluster out of `blender_addon/application/handlers/scene.py` into
  `blender_addon/application/handlers/scene_inspection_mixin.py`
- completed parent `TASK-159-03-01` because lifecycle/context, structural-read,
  and inspection/topology leaves are now all closed
- kept `SceneHandler` as the stable addon/RPC facade while preserving:
  - `inspect_object(...)`
  - `inspect_material_slots(...)`
  - `inspect_modifiers(...)`
  - `get_constraints(...)`
  - `inspect_mesh_topology(...)`
- moved the supporting inspection/constraint serialization helpers into the
  same mixin so the truth-read owner boundary is explicit

## Validation

- `python3 -m py_compile blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_inspection_mixin.py`
- `poetry run ruff check blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_inspection_mixin.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_get_mode_handler.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_inspect_modifiers.py tests/unit/tools/scene/test_get_constraints.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/test_handler_rpc_alignment.py -q`
  - result on this machine: `36 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_inspect_material_slots.py -q -rs`
  - result on this machine: `4 passed`
