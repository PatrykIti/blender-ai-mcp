# 344. TASK-135 creature gate contract hardening

Date: 2026-05-11

Task: `TASK-135-01`

## Summary

Closed post-review contract drift in the creature completion gate slice after a
code-level audit of the shipped `TASK-135-01` behavior.

## Changes

- Aligned aggregate creature pair roles with guided-flow cardinality so one
  registered aggregate object such as `Squirrel_Ears`, `Squirrel_FrontLegs`, or
  `Squirrel_HindLegs` can satisfy the corresponding required pair gate.
- Reblocked `final_completion` when targeted stale marking makes any required
  non-final gate stale, failed, or blocked.
- Kept gate-only `reference_part` blockers such as `eye_pair` off the
  `guided_register_part` path while still exposing bounded create/detail tools.
- Added targeted unit coverage for the pair-role aggregate path, final gate
  stale consistency, and `eye_pair` visibility/recommendation behavior.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py::test_required_part_pair_role_gate_accepts_aggregate_guided_role_object tests/unit/adapters/mcp/test_quality_gate_intake.py::test_mutating_tool_only_stales_gates_touching_affected_objects tests/unit/adapters/mcp/test_quality_gate_intake.py::test_reference_part_required_gate_recommends_bounded_create_without_role_registration tests/unit/adapters/mcp/test_visibility_policy.py::test_reference_part_required_gate_exposes_create_path_without_role_registration -q` (`6 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py -q` (`52 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q` (`245 passed`)
- `poetry run ruff check server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/transforms/quality_gate_verifier.py server/adapters/mcp/transforms/visibility_policy.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py`
- `PYTEST_ADDOPTS='-k creature_gate' poetry run python scripts/run_e2e_tests.py --skip-build` (`2 passed, 471 deselected`)
- `git diff --check`
