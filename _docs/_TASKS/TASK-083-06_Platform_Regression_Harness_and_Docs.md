# TASK-083-06: Platform Regression Harness and Docs

**Parent:** [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Close the baseline migration with regression coverage and documentation that prevents the repo from drifting back into 2.x-shaped runtime patterns.

---

## Repository Touchpoints

- `tests/unit/router/adapters/test_mcp_integration.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`
- `README.md`
- `ARCHITECTURE.md`

---

## Planned Work

### New Files To Create

- `tests/unit/adapters/mcp/test_surface_bootstrap.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_surface_compatibility.py`
- `_docs/_MCP_SERVER/fastmcp_3x_composition.md`

### Existing Files To Update

- `_docs/_TASKS/README.md`
  - link umbrella tasks to their new subtask breakdowns if needed
- `ARCHITECTURE.md`
  - document providers, transforms, and the composition root
- `README.md`
  - update runtime baseline and platform-layer explanation

---

## Test Scope

- bootstrap succeeds for the default surface
- surface exposes the expected providers and transforms
- router and dispatcher remain independent from public search-only surface listing
- old flat-catalog assumptions are caught by regression tests

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-083-06-01](./TASK-083-06-01_Core_Platform_Regression_Harness_Docs.md) | Core Platform Regression Harness and Docs | Core implementation layer |
| [TASK-083-06-02](./TASK-083-06-02_Tests_Platform_Regression_Harness_Docs.md) | Tests and Docs Platform Regression Harness and Docs | Tests, docs, and QA |

---

## Acceptance Criteria

- the MCP platform layer has its own regression harness
- the 3.x composition model is documented for future platform tasks
