# TASK-166-05-01: Expose Vision-Assist Input Budget Config

**Parent:** [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Replace the current hard-coded `vision_assist` input-character limit with explicit runtime config/env parsing and safe defaults.

## Repository Touchpoints

- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/vision/config.py`
- `server/infrastructure/config.py`
- `server/adapters/mcp/areas/reference.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/scripts/test_script_tooling.py`

## Implementation Notes

- Replace the current code-only `VISION_ASSIST_POLICY.max_input_chars` default
  with one runtime-owned config path while preserving a safe fallback.
- Keep fail-safe rejection semantics such as `input_budget_exceeded`
  deterministic even after config/env overrides are introduced.
- Ensure staged compare projection reads the effective configured limit through
  the existing `budget_control.max_input_chars` owner seam instead of leaking a
  second budget field.

## Acceptance Criteria

- the input-character budget is no longer a Python constant only
- operators can override it intentionally through runtime config
- the configured value flows through the existing runner owner seam without
  breaking the current staged compare `budget_control` contract

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/adapters/mcp/test_reference_images.py` for staged
  `budget_control.max_input_chars` projection

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
