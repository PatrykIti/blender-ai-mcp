# 304. TASK-159 scene context state-read slice

Date: 2026-05-04

## Summary

- completed `TASK-159-02-02-01` by extracting the `scene_context(...)`
  mode/selection read logic into
  `server/adapters/mcp/areas/scene_state_reads.py`
- kept `server/adapters/mcp/areas/scene.py` as the stable MCP facade and public
  registration host while reducing the monolithic adapter-state read branch
- preserved:
  - `scene_context(...)` public tool name and structured payload contract
  - existing `_scene_get_mode(...)` / `_scene_list_selection(...)` patch points
  - current read-only behavior and invalid-action error path

## Validation

- `python3 -m py_compile server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_state_reads.py`
- `poetry run ruff check server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_state_reads.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_context_mega.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
  - result on this machine: `30 passed`
