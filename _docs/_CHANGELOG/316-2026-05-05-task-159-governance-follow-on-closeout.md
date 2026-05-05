# 316. TASK-161 TASK-159 closeout alignment

Date: 2026-05-05
Version: -

## Summary

- opened and closed `TASK-161` as the explicit follow-on for the late
  `TASK-159` closeout drift instead of reopening children under the already
  closed parent
- finished the remaining `reference.py` seam closeout so staged reference tests
  now take the extracted helper modules as the direct proof seam instead of
  relying on facade-private helper imports
- aligned addon owner docs and proof lanes with the live mixin-based
  `SceneHandler`, including the current structural-read and origin payload
  shapes
- normalized the `Status / Board Update` sections across the `TASK-159*`
  family so the shipped modularization wave no longer reads as an active
  board-level workstream
- updated `TASK-159`, `_docs/_TASKS/README.md`, and `_docs/_CHANGELOG/README.md`
  so the closed parent, the completed follow-on, and the changelog index all
  agree on the final administrative state

## Validation

- `git diff --check` passed
- `poetry run pytest ./tests/unit`
  - current repo state fails during collection outside this docs-only scope:
    `tests/unit/adapters/mcp/test_reference_images.py` cannot import
    `_model_budget_bias` from `server.adapters.mcp.areas.reference`
- `poetry run python scripts/run_e2e_tests.py`
  - the full Blender-backed suite starts and runs, but the current repo state
    surfaces guided integration failures in
    `tests/e2e/integration/test_guided_gate_state_transport.py` and
    `tests/e2e/integration/test_guided_inspect_validate_handoff.py`; a quiet
    rerun did not finish with a final saved summary before this closeout was
    recorded
