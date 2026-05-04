# 308. TASK-159 scene create/configure slice

Date: 2026-05-04

## Summary

- completed `TASK-159-02-07` by extracting the grouped write-side
  `scene_create(...)` and `scene_configure(...)` logic from
  `server/adapters/mcp/areas/scene.py` into
  `server/adapters/mcp/areas/scene_create_configure.py`
- kept the public MCP facade in `scene.py` and preserved:
  - `scene_create(...)` public tool name and action vocabulary
  - `scene_configure(...)` public tool name and action vocabulary
  - existing `_scene_create_*` and `_scene_configure_*` thin patch seams
  - current structured response contracts and explicit validation errors
- kept grouped render/color/world writes aligned with the same roundtrip lane
  already used by the addon world/render branch

## Validation

- `python3 -m py_compile server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_create_configure.py`
- `poetry run ruff check server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/scene_create_configure.py`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_create_mega.py tests/unit/tools/scene/test_scene_configure_mega.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
  - result on this machine: `65 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_configure_roundtrip.py -q -rs`
  - result on this machine: `2 passed`
