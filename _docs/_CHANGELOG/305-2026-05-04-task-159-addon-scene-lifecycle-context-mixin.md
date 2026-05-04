# 305. TASK-159 addon scene lifecycle/context mixin

Date: 2026-05-04

## Summary

- completed `TASK-159-03-01-01` by splitting the early lifecycle and
  mode/selection context-read cluster out of
  `blender_addon/application/handlers/scene.py` into
  `blender_addon/application/handlers/scene_lifecycle_context_mixin.py`
- kept `SceneHandler` as the stable addon/RPC facade while preserving:
  - `list_objects(...)`
  - `delete_object(...)`
  - `clean_scene(...)`
  - `duplicate_object(...)`
  - `set_active_object(...)`
  - `get_mode(...)`
  - `list_selection(...)`
- preserved object-mode guards, selection mutation behavior, and the current
  context payload/result shapes

## Validation

- `python3 -m py_compile blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_lifecycle_context_mixin.py`
- `poetry run ruff check blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_lifecycle_context_mixin.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_get_mode_handler.py tests/unit/tools/scene/test_scene_tools.py tests/unit/tools/scene/test_scene_tools_extended.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_handler_rpc_alignment.py -q`
  - result on this machine: `43 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_clean_scene.py -q -rs`
  - result on this machine: `1 passed`
