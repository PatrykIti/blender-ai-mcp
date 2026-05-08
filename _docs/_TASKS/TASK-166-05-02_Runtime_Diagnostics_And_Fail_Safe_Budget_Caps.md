# TASK-166-05-02: Runtime Diagnostics And Fail-Safe Budget Caps

**Parent:** [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Surface configured and effective compare budgets in diagnostics while keeping fail-safe caps that prevent accidental unbounded payloads.

## Repository Touchpoints

- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Acceptance Criteria

- runtime diagnostics show configured vs effective compare budgets
- hard safety caps still prevent pathological payload growth
