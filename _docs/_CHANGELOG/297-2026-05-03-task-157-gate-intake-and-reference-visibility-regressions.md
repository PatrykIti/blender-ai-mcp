# 297. TASK-157 gate intake and reference visibility regressions

Date: 2026-05-03

## Summary

- changed guided quality-gate intake so a later proposal replaces only the
  active proposal-source slice instead of overwriting the whole session
  `active_gate_plan`, which now preserves existing
  `reference_understanding` gates, template gates, and verifier-updated
  statuses/blockers
- tightened relation-pair verification so attachment/support/symmetry gates
  without explicit `target_objects` no longer bind to an unrelated sole
  candidate pair unless the remaining meaningful target tokens still match the
  candidate semantics
- made `refresh_reference_understanding_summary_async(...)` reapply FastMCP
  visibility immediately after RU-driven gate/summary mutations, and extended
  the regression pack with unit coverage plus live e2e checks for proposal
  merge preservation and reference-visibility refresh

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `98 passed`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k 'reference_understanding_transport_roundtrip or reference_understanding_refresh_replaces_gate_slice or later_goal_gate_proposal_preserves_reference_understanding_gates' tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
  - result on this machine: `6 passed, 8 deselected`
