# TASK-166-05: Configurable Vision-Assist Budgets And Runtime Overrides

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Expose compare-related `vision_assist` budgets and runtime overrides as config/env instead of one hard-coded assistant policy.

## Completion Summary

- `TASK-166-05-01` is now complete:
  - `VISION_MAX_INPUT_CHARS` is runtime-owned and flows through config,
    runtime, runner enforcement, staged truth trimming, and
    `budget_control.max_input_chars`
- `TASK-166-05-02` is now complete:
  - runtime config preserves configured budget intent while exposing effective
    fail-safe-clipped image/input/output limits
  - runner envelopes and staged compare / iterate `budget_control` report
    configured vs effective values and clipping fields
  - compact orchestrator feedback carries a bounded uncertainty note when
    fail-safe clipping occurs

## Repository Touchpoints

- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/contracts/reference.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/scripts/test_script_tooling.py`

## Implementation Notes

- The current fixed `VISION_ASSIST_POLICY.max_input_chars=12000` should become
  explicit runtime config.
- Keep safe defaults and fail-safe upper bounds.
- Diagnostics must expose configured vs effective compare budgets.
- The runtime-owned budget source must be consumed consistently by
  `server/adapters/mcp/vision/runner.py`,
  `server/adapters/mcp/areas/reference.py`, and
  `server/adapters/mcp/areas/reference_planner.py`; do not leave independent
  direct reads of `VISION_ASSIST_POLICY` behind in staged compare assembly or
  planner helpers.
- The current runtime config exposes `max_images` and `max_tokens` but not a
  compare-path `max_input_chars` home, so this family must define that config
  ownership before rewiring runner rejection and staged budget projection.
- `server/adapters/mcp/vision/runtime.py` remains the bridge from
  infrastructure `Config` into `VisionRuntimeConfig`, so budget/env changes are
  not complete until that seam and its runtime-config tests stay aligned.

## Current Flow Integration

- The new knobs should feed one runtime-owned budget source exposed through the
  `server/adapters/mcp/vision/runner.py` seam and reused by staged compare
  helpers.
- `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` should continue to surface the final
  chosen values through `budget_control`, but they should no longer depend on
  one code-only constant.
- More detailed configured-vs-effective budget reporting may surface additively
  through compare diagnostics or compact feedback notes, but it must not replace
  the existing `budget_control` surface.
- Configurable budgets are a support mechanism for the packeted family, not the
  primary replacement for packet decomposition.

## Pseudocode

```text
runtime_budget = resolve_runtime_budget(config, env, defaults)
effective_budget = clamp_budget(runtime_budget, fail_safe_caps)
runner = project_effective_budget_into_vision_runner(effective_budget)
staged_compare = project_budget_state_into_budget_control(runner, effective_budget)
```

## Runtime / Security Contract Notes

- Config/env overrides must not silently disable fail-safe caps.
- Public staged compare / iterate responses keep one canonical budget surface:
  `budget_control`, with additive diagnostics only when extra transparency is
  justified.
- Budget overrides that change client-visible behavior must remain explicit and
  transport-safe across stdio and Streamable HTTP.

## Acceptance Criteria

- compare input budgets are operator-configurable
- diagnostics explain configured and effective budget values
- detailed budget visibility remains additive to the existing staged contract
- runner rejection, staged truth trimming, and `budget_control` all consume one
  resolved runtime budget instead of partially independent limits

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/adapters/mcp/test_reference_images.py` for staged budget
  projection behavior
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- relevant script/runtime operator notes when env/config knobs are added
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- runtime input-budget config shipped in changelog `330`
- configured/effective diagnostics and fail-safe caps shipped in changelog `334`

## Status / Board Update

- `TASK-166-05` is closed; no open direct budget leaves remain
- promoted `TASK-166` remains open for `TASK-166-04-02` and `TASK-166-06`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
