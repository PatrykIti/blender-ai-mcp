# 289. TASK-157 transport parity and live support/symmetry E2E

Date: 2026-05-03

## Summary

- extended the real `test_guided_gate_state_transport.py` harness so
  `support_contact` and `symmetry_pair` now run over Streamable HTTP as well as
  stdio, closing the remaining transport parity gap inside the shipped
  TASK-157 owner lane
- added dedicated Blender-backed public-surface E2E in
  `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py` for
  `reference_compare_stage_checkpoint(...)` on unsupported support pairs and
  asymmetric symmetry pairs, including assertions over `truth_bundle`,
  `truth_followup`, and `correction_candidates`
- refreshed TASK/test-board docs so the owner-lane validation surface now
  reflects the stronger transport and live public-surface coverage

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `82 passed`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_goal_derived_gate_building_completion.py tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py -q`
  - result on this machine: `11 passed`
