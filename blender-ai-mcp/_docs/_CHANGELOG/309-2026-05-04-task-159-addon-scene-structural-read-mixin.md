# 309. TASK-159 addon scene structural-read mixin

Date: 2026-05-04

## Summary

- completed `TASK-159-03-01-02` by splitting the addon snapshot and
  structural-read cluster out of
  `blender_addon/application/handlers/scene.py` into
  `blender_addon/application/handlers/scene_structural_read_mixin.py`
- kept `SceneHandler` as the stable addon/RPC facade while preserving:
  - `snapshot_state(...)`
  - `get_hierarchy(...)`
  - `get_bounding_box(...)`
  - `get_origin_info(...)`
- moved the supporting `_vec_to_list(...)`, `_gather_mesh_stats(...)`,
  `_get_object_or_raise(...)`, `_get_bbox_data(...)`, and `_round_values(...)`
  helpers with the same structural-read owner branch

## Validation

- `python3 -m py_compile blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_structural_read_mixin.py`
- `poetry run ruff check blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_structural_read_mixin.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_snapshot_state_visibility.py tests/unit/tools/test_handler_rpc_alignment.py -q`
  - result on this machine: `16 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_snapshot_tools.py -q -rs`
  - result on this machine: `3 passed`
