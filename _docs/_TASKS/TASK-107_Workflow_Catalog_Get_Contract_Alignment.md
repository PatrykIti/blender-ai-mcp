# TASK-107: Workflow Catalog Get Contract Alignment

**Priority:** 🟡 Medium  
**Category:** MCP / Structured Contract Alignment  
**Estimated Effort:** Small  
**Dependencies:** None  
**Status:** ✅ Done

**Completion Summary:** `WorkflowCatalogResponseContract` now accepts the top-level `steps_count` field returned by `workflow_catalog(action="get")`, preventing a Pydantic `extra_forbidden` failure on valid workflow-definition responses.

---

## Objective

Keep the MCP contract for `workflow_catalog(action="get")` aligned with the real handler response.

---

## Problem

The handler returned:

- `workflow_name`
- `steps_count`
- `workflow`

but the MCP contract did not include `steps_count`, so a valid workflow-definition response failed contract validation.

---

## Solution

Extend `WorkflowCatalogResponseContract` with the missing `steps_count` field and add a regression test for the `get` action path.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/workflow_catalog.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py`

---

## Acceptance Criteria

- `workflow_catalog(action="get")` accepts the top-level `steps_count` field
- valid workflow-definition responses no longer fail with `extra_forbidden`
