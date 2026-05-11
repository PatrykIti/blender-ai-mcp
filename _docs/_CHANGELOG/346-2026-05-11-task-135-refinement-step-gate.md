# 346. TASK-135 refinement step gate

Date: 2026-05-11

Task: `TASK-135-03-01`

## Summary

Shipped the first low-poly creature refinement slice by making
`refine_low_poly_forms` an explicit guided-flow step on the existing generic
gate and guided-family contracts.

## Changes

- Added `refine_low_poly_forms` to `GuidedFlowStepLiteral` and the guided
  session state policy.
- Let creature sessions enter refinement from secondary-role registration or
  checkpoint iteration only when normalized profile/refinement blockers are
  ready and required seam/support blockers plus stale spatial state are clear.
- Kept `allowed_families` on the existing `secondary_parts`,
  `attachment_alignment`, and `reference_context` vocabulary.
- Narrowed the refinement-step build surface to bounded mesh/profile and
  attachment tools, while keeping primary-mass creation and finish-heavy tools
  hidden by default.
- Added unit coverage for state round-trip, step advancement, seam/stale
  blocking, checkpoint transition, visibility policy, and guided-mode
  diagnostics.
- Updated prompt, MCP, test, task, board, and README docs for the shipped
  refinement state gate.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py -q` (`75 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_public_surface_docs.py -q` (`87 passed`)
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q` (`17 passed`)
- `poetry run ruff check server/adapters/mcp/contracts/guided_flow.py server/adapters/mcp/session_capabilities_flow.py server/adapters/mcp/session_capabilities_registry.py server/adapters/mcp/transforms/visibility_policy.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `git diff --check`
