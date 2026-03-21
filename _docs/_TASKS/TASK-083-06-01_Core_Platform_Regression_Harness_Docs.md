# TASK-083-06-01: Core Platform Regression Harness and Docs

**Parent:** [TASK-083-06](./TASK-083-06_Platform_Regression_Harness_and_Docs.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Implement the core code changes for **Platform Regression Harness and Docs**.

---

## Repository Touchpoints

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

## Acceptance Criteria

- the MCP platform layer has its own regression harness
- the 3.x composition model is documented for future platform tasks
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
