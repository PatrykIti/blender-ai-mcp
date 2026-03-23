# TASK-108-03: RPC Result Type Alignment for Server Handlers

**Parent:** [TASK-108](./TASK-108_Coverage_Expansion_For_Contracts_MCP_Areas_RPC_And_Surface_Runtime.md)  
**Status:** ⬜ To Do  
**Priority:** 🔴 High  
**Depends On:** TASK-106

---

## Objective

Expand regression coverage for server-side handlers that narrow `RpcResponse.result` into strict string, dict, or list shapes.

---

## Repository Touchpoints

- `server/application/tool_handlers/_rpc_utils.py`
- `server/application/tool_handlers/modeling_handler.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/application/tool_handlers/collection_handler.py`
- `server/application/tool_handlers/material_handler.py`
- `server/application/tool_handlers/extraction_handler.py`
- `server/application/tool_handlers/uv_handler.py`
- `tests/unit/tools/`

---

## Planned Work

- add direct tests for `_rpc_utils.py` success and failure paths on missing, wrong-type, and malformed result payloads
- add representative handler tests for string, dict, list-of-dicts, and paged payload expectations
- use addon-shaped fixtures for methods that already proved drift-prone, especially modeling and structured inspection paths
- pin explicit error messages for result-type mismatches so failures stay actionable

---

## Acceptance Criteria

- every narrowing helper in `_rpc_utils.py` is covered on both success and error branches
- representative handlers across scene/modeling/mesh/collection/material/extraction/uv have tests for the expected result type
- no critical handler path relies on an unverified implicit result coercion
- regressions of the form "expected string, got dict" or "expected list item type X" are caught by unit tests
