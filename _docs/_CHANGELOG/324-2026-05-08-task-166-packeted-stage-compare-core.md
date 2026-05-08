# 324. TASK-166 packeted stage compare core

Date: 2026-05-08

## Summary

- replaced the old monolithic staged compare request shape in
  `server/adapters/mcp/areas/reference.py` with bounded packet-local compare
  execution on the existing `reference_compare_stage_checkpoint(...)` /
  `reference_iterate_stage_checkpoint(...)` public tools
- added typed packet contracts in
  `server/adapters/mcp/contracts/reference.py`:
  - `ReferenceComparePacketContract`
  - `ReferenceCompareDiagnosticsContract`
  - staged compare / iterate now carry additive `compare_diagnostics`
- introduced deterministic compare-plan helpers in
  `server/adapters/mcp/areas/reference_planner.py` that:
  - classify the staged run as `simple`, `complex`, or `super_complex`
  - build stable packet ids from packet-local view/scope/reference/capture
    slices
  - synthesize successful packet results back into one compact
    `VisionAssistContract`
- narrowed packet-local truth payloads before each `vision_assist` call so
  collection/object-set compare no longer sends every truth pair in every
  request by default
- projected packet evidence/uncertainty into
  `reference_orchestrator_feedback.evidence_summary` and
  `reference_orchestrator_feedback.uncertainty_notes` without creating a second
  public response family
- kept packet diagnostics profile-aware on the staged public surface:
  - emitted on `preset_profile="rich"`
  - emitted on multi-packet synthesis, packet uncertainty/failure, or budget
    pressure
  - omitted on clean compact single-packet runs
- updated docs/tests/task state for the first active TASK-166 delivery slice

## Runtime / Contract Notes

- The public tool names stay the same; packeting is an internal staged compare
  refactor that projects back onto the existing compare / iterate contracts.
- `compare_diagnostics` is additive and bounded. It does not replace
  `truth_followup`, `correction_candidates`, `budget_control`, or
  `reference_orchestrator_feedback`.
- This slice ships packet planning, packet-local execution, packet synthesis,
  and compact diagnostics projection. Follow-on TASK-166 leaves still own the
  deeper prompt/parser contract split, always-on deterministic CV enrichers,
  optional heavier sidecars, and runtime-configurable compare budgets.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
