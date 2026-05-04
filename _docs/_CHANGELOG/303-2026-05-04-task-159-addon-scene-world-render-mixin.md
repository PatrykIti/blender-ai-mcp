# 303. TASK-159 addon scene world/render mixin

Date: 2026-05-04

## Summary

- completed `TASK-159-03-05` by splitting the world/render/color-management
  cluster out of `blender_addon/application/handlers/scene.py` into
  `blender_addon/application/handlers/scene_world_render_mixin.py`
- kept `SceneHandler` as the stable RPC facade and preserved:
  - render settings inspection/configuration payloads
  - color-management inspection/configuration payloads
  - world/background inspection/configuration payloads
  - `node_graph_reference` and `node_graph_handoff` semantics
- reduced the addon scene monolith without widening the supported
  `scene_configure(...)` boundary or changing reject-unknown behavior for world
  node-graph payloads

## Validation

- `python3 -m py_compile blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_world_render_mixin.py`
- `poetry run ruff check blender_addon/application/handlers/scene.py blender_addon/application/handlers/scene_world_render_mixin.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_configure_handler.py tests/unit/tools/test_handler_rpc_alignment.py -q`
  - result on this machine: `21 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_configure_roundtrip.py -q -rs`
  - result on this machine: `2 passed`
