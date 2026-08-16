# 306. TASK-159 reference current-view compare split

Date: 2026-05-04

## Summary

- completed `TASK-159-01-05` by splitting the current-view compare path out of
  `server/adapters/mcp/areas/reference.py` into:
  - `server/adapters/mcp/areas/reference_current_view.py`
  - `server/adapters/mcp/areas/reference_checkpoint_compare.py`
- kept `reference.py` as the public MCP facade while preserving:
  - `reference_compare_current_view(...)` public behavior
  - shared checkpoint compare response assembly
  - target-object / target-view reference selection
  - current-view prompt hint shaping and bounded checkpoint persistence
- kept the extraction narrow enough that staged compare/iterate orchestration
  stayed in `reference.py` instead of being partially duplicated or widened

## Validation

- `python3 -m py_compile server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_checkpoint_compare.py server/adapters/mcp/areas/reference_current_view.py`
- `poetry run ruff check server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_checkpoint_compare.py server/adapters/mcp/areas/reference_current_view.py`
- `poetry run mypy server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_checkpoint_compare.py server/adapters/mcp/areas/reference_current_view.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `81 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_get_viewport.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py -q -rs`
  - result on this machine: `3 passed`
