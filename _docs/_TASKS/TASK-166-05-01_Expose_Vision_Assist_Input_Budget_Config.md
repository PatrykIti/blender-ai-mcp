# TASK-166-05-01: Expose Vision-Assist Input Budget Config

**Parent:** [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Replace the current hard-coded `vision_assist` input-character limit with explicit runtime config/env parsing and safe defaults.

## Completion Summary

- added runtime-owned `VISION_MAX_INPUT_CHARS` wiring through
  infrastructure `Config`, `VisionRuntimeConfig`, and the bounded
  `vision_assist` runner
- runner rejection for `input_budget_exceeded` now uses the resolved runtime
  limit instead of a compare-only Python constant
- staged compare truth trimming and top-level `budget_control.max_input_chars`
  now read the same resolved runtime limit, so packet assembly and runner
  enforcement no longer drift on input-budget ownership
- operator launch examples now expose `VISION_MAX_INPUT_CHARS` alongside the
  existing image/token knobs

## Repository Touchpoints

- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/adapters/mcp/vision/config.py`
- `server/infrastructure/config.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/scripts/test_script_tooling.py`

## Implementation Notes

- Replace the current code-only `VISION_ASSIST_POLICY.max_input_chars` default
  with one runtime-owned config path while preserving a safe fallback.
- Define where the new input-character budget lives in runtime config first; the
  current `VisionRuntimeConfig` exposes `max_images` / `max_tokens` but no
  `max_input_chars` owner yet.
- Keep `server/adapters/mcp/vision/runtime.py` aligned with that new config
  field so `build_vision_runtime_config()` continues to bridge env/config values
  into the live runtime rather than leaving the new budget stranded in the
  model layer.
- Keep fail-safe rejection semantics such as `input_budget_exceeded`
  deterministic even after config/env overrides are introduced.
- Update staged compare assembly and planner budget helpers to read the same
  effective input-budget source rather than leaving direct fallback reads of the
  old constant in `reference.py` or `reference_planner.py`.
- Ensure staged compare projection reads the effective configured limit through
  the existing `budget_control.max_input_chars` owner seam instead of leaking a
  second budget field.

## Acceptance Criteria

- the input-character budget is no longer a Python constant only
- operators can override it intentionally through runtime config
- the configured value flows through the existing runner owner seam without
  breaking the current staged compare `budget_control` contract
- staged compare assembly and planner helpers project the same effective limit
  instead of diverging from runner enforcement

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/adapters/mcp/test_reference_images.py` for staged
  `budget_control.max_input_chars` projection
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- relevant runtime/operator notes for new config or env knobs
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- runtime-owned input-budget config shipped through `_docs/_CHANGELOG/330*`
  and later budget-diagnostics hardening.

## Status / Board Update

- parent `TASK-166` and this leaf are aligned as `✅ Done`; broader budget
  diagnostics also shipped under `TASK-166-05-02`.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
