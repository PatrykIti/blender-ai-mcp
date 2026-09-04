# 302. TASK-159 addon scene utility mixins

Date: 2026-05-04

## Summary

- completed `TASK-159-03-04` by splitting the addon utility cluster out of
  `blender_addon/application/handlers/scene.py` into focused mixins:
  - `blender_addon/application/handlers/scene_creation_utility_mixin.py`
  - `blender_addon/application/handlers/scene_mode_visibility_utility_mixin.py`
  - `blender_addon/application/handlers/scene_custom_property_utility_mixin.py`
- kept `SceneHandler` as the stable addon/RPC facade by composing the new
  mixins instead of changing the handler entrypoint or the server-side
  integration path
- preserved:
  - light/camera/empty creation defaults and return values
  - object-mode validation plus rename/hide/show/isolate side effects
  - structured custom-property read/write delivery
- closed task docs for `TASK-159-03-04` and leaves
  `TASK-159-03-04-01` through `TASK-159-03-04-03` while keeping parent
  `TASK-159` / `TASK-159-03` open for the remaining addon scene branches

## Validation

- `python3 -m py_compile blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_creation_utility_mixin.py blender_addon/application/handlers/scene_mode_visibility_utility_mixin.py blender_addon/application/handlers/scene_custom_property_utility_mixin.py`
- `poetry run ruff check blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_creation_utility_mixin.py blender_addon/application/handlers/scene_mode_visibility_utility_mixin.py blender_addon/application/handlers/scene_custom_property_utility_mixin.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mode.py tests/unit/tools/scene/test_scene_construction.py tests/unit/tools/scene/test_hide_object.py tests/unit/tools/scene/test_show_all_objects.py tests/unit/tools/scene/test_rename_object.py tests/unit/tools/scene/test_isolate_object.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
  - result on this machine: `72 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_hide_object.py tests/e2e/tools/scene/test_show_all_objects.py tests/e2e/tools/scene/test_rename_object.py tests/e2e/tools/scene/test_isolate_object.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py tests/e2e/tools/scene/test_scene_view_diagnostics.py tests/e2e/tools/scene/test_scene_utility_workflow.py -q -rs`
  - result on this machine: `17 passed`
