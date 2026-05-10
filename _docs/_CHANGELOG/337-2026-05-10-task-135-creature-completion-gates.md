# 337. TASK-135 creature completion gates

Date: 2026-05-10

Task: `TASK-135-01`

## Summary

Closed the first `TASK-135` implementation slice by tightening guided creature
completion on the existing `TASK-157` quality-gate surface.

## Changes

- Added repo-owned creature visual-role templates for body, head, tail, snout,
  ears, eyes, forelegs, and hindlegs.
- Kept `eye_pair` gate-only for this slice instead of adding a new guided build
  role.
- Materialized checkpoint-derived required creature seams as
  `reference_checkpoint` gates, so unresolved `floating_gap` seams block final
  completion through the same `active_gate_plan`, `completion_blockers`, and
  `recommended_bounded_tools` surfaces.
- Updated prompt, MCP, vision, tool-summary, test, and task docs for the stricter
  creature blockout completion contract.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py -q` (`13 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_materializes_creature_completion_gates_from_truth tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_projects_gate_state_from_checkpoint_truth_without_prior_relation_call -q` (`2 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q` (`117 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q` (`12 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py -q` (`77 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q` (`10 passed`)
- `poetry run ruff check server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
- `PYTHONPATH=. poetry run pytest ./tests/unit` (`3313 passed`)
- `PYTEST_ADDOPTS='-k creature_gate_repair_macro_clears_tail_seam_blocker' poetry run python scripts/run_e2e_tests.py --skip-build` (`1 passed, 470 deselected`)
- `poetry run python -u scripts/run_e2e_tests.py` (`468 passed, 3 skipped`)
- `git diff --check`
