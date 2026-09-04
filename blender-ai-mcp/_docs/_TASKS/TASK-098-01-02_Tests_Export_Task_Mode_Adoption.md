# TASK-098-01-02: Tests and Docs Export Task Mode Adoption

**Parent:** [TASK-098-01](./TASK-098-01_Export_Task_Mode_Adoption.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-098-01-01](./TASK-098-01-01_Core_Export_Task_Mode_Adoption.md)

---

## Objective

Add regression coverage and documentation updates for export task-mode adoption.

---

## Repository Touchpoints

- `tests/unit/tools/export/`
- `tests/unit/adapters/mcp/`
- `tests/unit/adapters/rpc/`
- `tests/e2e/tools/export/`
- `_docs/`

---

## Planned Work

### Regression Scenarios

1. background happy path for each adopted export tool
2. cancellation and timeout path for at least one export tool
3. foreground compatibility path for non-task execution
4. no regression on existing export validation and path handling

### Test Asset Reuse

- extend `tests/unit/tools/export/test_export_tools.py`
- add MCP/task-mode coverage under `tests/unit/adapters/mcp/`
- add RPC lifecycle coverage under `tests/unit/adapters/rpc/`
- selectively extend `tests/e2e/tools/export/test_export_tools.py` once task submission coverage is ready

---

## Acceptance Criteria

- export task-mode regressions are covered and documented
- existing export behavior remains stable in foreground mode
