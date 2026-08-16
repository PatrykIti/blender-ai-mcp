# 138 - 2026-03-23: Coverage expansion for contracts, MCP areas, RPC alignment, and surface runtime

## Summary

Closed the next cross-cutting coverage wave for high-value regression surfaces:

- structured MCP contract payload parity
- MCP area main public action paths
- server-side RPC result narrowing helpers and representative handlers
- FastMCP profile/listing/visibility/pagination behavior

This pass focused on catching drift at the product boundaries where recent regressions had already appeared:

- contract vs handler payload mismatches
- missing or weak MCP wrapper behavior coverage
- strict RPC string/dict/list narrowing failures
- shaped surface exposure changes across profiles and phases

## Updated files

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py`
- `tests/unit/router/application/test_correction_audit.py`
- `tests/unit/tools/modeling/test_modeling_handler_rpc.py`
- `tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py`
- `tests/unit/tools/test_rpc_utils.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/tools/test_mcp_area_main_paths.py`
- `_docs/_TASKS/TASK-108_Coverage_Expansion_For_Contracts_MCP_Areas_RPC_And_Surface_Runtime.md`
- `_docs/_TASKS/TASK-108-01_Contract_Payload_Parity_Across_MCP_Contracts.md`
- `_docs/_TASKS/TASK-108-02_Main_Action_Path_Coverage_For_MCP_Areas.md`
- `_docs/_TASKS/TASK-108-03_RPC_Result_Type_Alignment_For_Server_Handlers.md`
- `_docs/_TASKS/TASK-108-04_Surface_Profile_List_Tools_Pagination_And_Visibility_Matrix.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Validation

```bash
poetry run pytest tests/unit/adapters/mcp/test_contract_base.py tests/unit/adapters/mcp/test_delivery_strategy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_pagination_policy.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/router/application/test_router_contracts.py tests/unit/router/application/test_correction_audit.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/mesh/test_mesh_contracts.py tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py tests/unit/tools/workflow_catalog/test_workflow_catalog_assistants.py tests/unit/tools/collection/test_collection_mcp_tools.py tests/unit/tools/material/test_material_mcp_tools.py tests/unit/tools/extraction/test_extraction_mcp_tools.py tests/unit/tools/system/test_system_mcp_tools.py tests/unit/tools/modeling/test_modeling_handler_rpc.py tests/unit/tools/test_rpc_utils.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/tools/test_mcp_area_main_paths.py -q
poetry run ruff check tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py tests/unit/router/application/test_correction_audit.py tests/unit/tools/modeling/test_modeling_handler_rpc.py tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py tests/unit/tools/test_rpc_utils.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/tools/test_mcp_area_main_paths.py
```

Result:

- targeted regression suite: `152 passed`
- targeted lint checks: `All checks passed`
