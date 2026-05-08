# TASK-166-05: Configurable Vision-Assist Budgets And Runtime Overrides

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Expose compare-related `vision_assist` budgets and runtime overrides as config/env instead of one hard-coded assistant policy.

## Repository Touchpoints

- `server/adapters/mcp/vision/runner.py`
- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/areas/reference.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/scripts/test_script_tooling.py`

## Implementation Notes

- The current fixed `VISION_ASSIST_POLICY.max_input_chars=12000` should become
  explicit runtime config.
- Keep safe defaults and fail-safe upper bounds.
- Diagnostics must expose configured vs effective compare budgets.

## Current Flow Integration

- The new knobs should feed the existing `VISION_ASSIST_POLICY` owner seam in
  `vision/runner.py`.
- `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` should continue to surface the final
  chosen values through `budget_control`, but they should no longer depend on
  one code-only constant.
- More detailed configured-vs-effective budget reporting may surface additively
  through compare diagnostics or compact feedback notes, but it must not replace
  the existing `budget_control` surface.
- Configurable budgets are a support mechanism for the packeted family, not the
  primary replacement for packet decomposition.

## Acceptance Criteria

- compare input budgets are operator-configurable
- diagnostics explain configured and effective budget values
- detailed budget visibility remains additive to the existing staged contract

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/adapters/mcp/test_reference_images.py` for staged budget
  projection behavior

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- relevant script/runtime operator notes when env/config knobs are added

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when runtime budget
  overrides ship

## Status / Board Update

- keep parent `TASK-166` and this subtask aligned in `_docs/_TASKS/README.md`
- note explicitly whether config parsing, runtime diagnostics, and fail-safe
  caps all shipped together or remain split across open leaves

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
