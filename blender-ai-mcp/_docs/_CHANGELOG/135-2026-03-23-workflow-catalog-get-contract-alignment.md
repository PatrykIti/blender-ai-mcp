# 135 - 2026-03-23: Workflow catalog get contract alignment

**Status**: ✅ Completed  
**Type**: Bugfix / Contract Alignment  
**Task**: TASK-107

---

## Summary

Fixed a contract mismatch for `workflow_catalog(action="get")`.

The handler returned a top-level `steps_count` field, but the MCP contract did not define it, causing valid responses to fail Pydantic validation.

---

## Changes

- Added `steps_count` to `WorkflowCatalogResponseContract`.
- Added regression coverage for the `workflow_catalog(action="get")` MCP adapter path.

---

## Files Modified (high level)

- `server/adapters/mcp/contracts/workflow_catalog.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py`

---

## Validation

- `poetry run pytest tests/unit/router/application/test_router_contracts.py tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py -q`
