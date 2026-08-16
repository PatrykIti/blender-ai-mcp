# 283. Stage checkpoint planner view-diagnostics wiring

Date: 2026-05-01

## Summary

- wired staged `view_diagnostics_hints` into
  `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` using the same deterministic focus
  preset that drives silhouette/local-target selection
- fixed the planner/runtime gap where staged organic local-form cases could
  only reach `sculpt_region` in hand-built test payloads, while the real stage
  compare path always fell back to `inspect_only` with
  `view_diagnostics_required`
- added a regression that exercises the real stage-checkpoint assembler and
  proves `sculpt_region` becomes `ready` when staged view diagnostics are
  present and clear
- preserved the fail-safe path where missing staged view evidence still emits a
  typed `scene_view_diagnostics(...)` support requirement

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_context_bridge.py -q`
  - result on this machine: `116 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - result on this machine: `251 passed`
- `poetry run ruff check server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_reference_images.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/areas/reference.py`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/tools/sculpt/test_sculpt_tools.py -q -rs`
  - result on this machine: `19 passed`
