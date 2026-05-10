# TASK-166-05-02: Runtime Diagnostics And Fail-Safe Budget Caps

**Parent:** [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Surface configured and effective compare budgets in diagnostics while keeping fail-safe caps that prevent accidental unbounded payloads.

## Completion Summary

- Added explicit fail-safe caps for bounded vision execution:
  - `12` images
  - `48_000` serialized input characters
  - `8_192` output tokens
- `VisionRuntimeConfig` now keeps configured values while exposing effective
  clipped values and `budget_clip_fields` for runtime diagnostics.
- `run_vision_assist(...)`, local/external backend token caps, macro capture
  profile selection, staged truth trimming, and staged `budget_control` now use
  effective limits.
- Staged compare / iterate `budget_control` reports configured, effective, and
  fail-safe limits plus clipping fields; compact orchestrator feedback carries a
  bounded uncertainty note when fail-safe clipping occurs.
- `scripts/run_streamable_openrouter.sh` now defaults `VISION_MAX_TOKENS` to
  the fail-safe output cap instead of an intentionally oversized provider value.

## Repository Touchpoints

- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Implementation Notes

- Surface configured vs effective budget values through the existing
  `budget_control` seam and any additive `compare_diagnostics` field without
  making clients parse raw runner internals.
- Keep the staged compare assembler, planner budget helpers, and compact
  feedback projection aligned on one typed configured-vs-effective budget
  picture rather than recomputing ad-hoc diagnostics per caller.
- Keep fail-safe upper bounds explicit so operators can distinguish
  configured-budget intent from clipped effective runtime behavior.
- If budget clipping changes the next safe action, the compact
  `reference_orchestrator_feedback` projection should carry that as bounded
  uncertainty rather than a hidden transport-only detail.

## Acceptance Criteria

- runtime diagnostics show configured vs effective compare budgets
- hard safety caps still prevent pathological payload growth
- per-run budget detail can surface additively in richer compare diagnostics
  while `budget_control` remains the existing top-level operator surface

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py` when budget
  diagnostics change a client-visible staged contract

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- shipped in `_docs/_CHANGELOG/334-2026-05-10-task-166-runtime-budget-diagnostics-and-fail-safe-caps.md`

## Status / Board Update

- parent `TASK-166-05` is now ready to close because both config parsing and
  configured-vs-effective diagnostics have shipped
- later complexity-tier and public transparency cleanup closed under
  `TASK-166-04-02` and `TASK-166-06`; changelog `336` closed the promoted
  `TASK-166` umbrella

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
