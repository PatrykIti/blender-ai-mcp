# 391 - 2026-05-31 - TASK-179-03 auxiliary-channel transmission

## Summary

- Added default-off `VISION_TRANSMIT_AUX_CHANNELS` runtime wiring for bounded
  depth, normal, and object-ID auxiliary images.
- Appended canonical focus-view auxiliary captures as typed
  `view_kind="depth"`, `view_kind="normal"`, and `view_kind="object_id"`
  images, with advisory per-image captions and budget-drop metadata.
- Kept auxiliary captures out of default payloads, dropped them before primary
  captures when image budgets are tight, and kept packet complexity based on
  primary captures only.
- Extended Blender `USER_PERSPECTIVE` support to depth and normal passes so
  staged auxiliary renders mirror the already-framed active viewport.
- Hardened the temporary-camera mirror path so `USER_PERSPECTIVE` depth/normal
  passes restore active object and selected-object state after rendering.
- Threaded resolved model capabilities into generic external payload
  `requested_json_keys` so weak-model schemas and prompt payloads agree when
  `findings` is dropped.

## Validation

- `poetry run ruff check server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_compare_packets.py server/adapters/mcp/vision/capture.py server/adapters/mcp/vision/capture_runtime.py server/adapters/mcp/vision/integration.py server/adapters/mcp/vision/prompting.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/e2e/tools/scene/test_scene_get_depth_pass.py tests/e2e/tools/scene/test_scene_get_normal_pass.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTEST_ADDOPTS='-k "depth_pass_supports_user_perspective_view or normal_pass_supports_user_perspective_view"' poetry run python scripts/run_e2e_tests.py`
