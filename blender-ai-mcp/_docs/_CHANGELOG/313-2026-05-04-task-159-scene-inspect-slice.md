# 313. TASK-159 scene inspect slice

Date: 2026-05-04

## Summary

- completed `TASK-159-02-02-03` by extracting the `scene_inspect(...)` action
  matrix and its helper logic from `server/adapters/mcp/areas/scene.py` into
  `server/adapters/mcp/areas/scene_inspect.py`
- completed parent `TASK-159-02-02` because context/selection, structural
  reads, and inspect action-matrix leaves are now all closed
- kept `scene.py` as the stable MCP facade while preserving:
  - `scene_inspect(...)` public action vocabulary
  - current `_scene_inspect_*` and `_scene_get_constraints(...)` thin seams
  - typed response contracts and assistant-summary behavior

## Validation

- `python3 -m py_compile server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_inspect.py`
- `poetry run ruff check server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_inspect.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_inspect_mega.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/scene/test_scene_inspect_modifiers.py tests/unit/tools/scene/test_get_constraints.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
  - result on this machine: `65 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_inspect_material_slots.py -q -rs`
  - result on this machine: `4 passed`
