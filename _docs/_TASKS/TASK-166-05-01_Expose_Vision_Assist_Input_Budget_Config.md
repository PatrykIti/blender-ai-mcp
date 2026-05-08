# TASK-166-05-01: Expose Vision-Assist Input Budget Config

**Parent:** [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Replace the current hard-coded `vision_assist` input-character limit with explicit runtime config/env parsing and safe defaults.

## Repository Touchpoints

- `server/adapters/mcp/vision/runner.py`
- `server/infrastructure/config.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/scripts/test_script_tooling.py`

## Acceptance Criteria

- the input-character budget is no longer a Python constant only
- operators can override it intentionally through runtime config
