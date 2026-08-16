# 307. TASK-159 scene structural-read slice

Date: 2026-05-04

## Summary

- completed `TASK-159-02-02-02` by extending
  `server/adapters/mcp/areas/scene_state_reads.py` to own the execution logic
  for:
  - `scene_snapshot_state(...)`
  - `scene_compare_snapshot(...)`
  - `scene_get_hierarchy(...)`
  - `scene_get_bounding_box(...)`
  - `scene_get_origin_info(...)`
- kept `server/adapters/mcp/areas/scene.py` as the stable MCP facade and left
  the assistant-summary follow-up seam in place while reducing the read-heavy
  monolithic body
- preserved snapshot/diff contracts and structural-read payloads without
  changing public tool names or helper-facing semantics

## Validation

- `python3 -m py_compile server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_state_reads.py`
- `poetry run ruff check server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_state_reads.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
  - result on this machine: `54 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_snapshot_tools.py -q -rs`
  - result on this machine: `3 passed`
