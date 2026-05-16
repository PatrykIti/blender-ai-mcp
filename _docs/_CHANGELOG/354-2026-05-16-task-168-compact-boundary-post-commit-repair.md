# 354. TASK-168 compact-boundary post-commit repair

Date: 2026-05-16

## Summary

Closed the remaining post-commit `TASK-168` drift found after the initial
runtime-confinement repair. The pass focused on the already shipped guided
confinement and staged-reference seams rather than adding a new owner path.

The repair pass:

- kept normal clean `compact` staged compare/iterate responses controller-sized
  by omitting heavy `truth_bundle`, `truth_followup`, `correction_candidates`,
  and rich `planner_detail` unless the caller requests rich detail, the response
  is a hard-failure/error path, or packet uncertainty requires escalation
- preserved additive top-level `compare_diagnostics` for packet provenance,
  multi-packet synthesis, model-budget pressure, packet uncertainty, and rich
  delivery without treating diagnostics presence as permission to emit every
  heavy nested detail field
- made `guided_register_part(...)` missing-object and unavailable-scene
  validation failures return the same typed fail-closed status surface as
  invalid-role and naming-policy blocks
- refreshed prompt/public docs so compact clients prioritize
  `reference_orchestrator_feedback`, top-level focus/planner summaries,
  `action_hints`, and `compare_diagnostics` instead of waiting for rich-only
  truth/candidate detail on normal compact paths

## Validation

- targeted owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
  - result: `160 passed`
- broad repo unit proof outside the sandbox:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - result: `3447 passed`
- repo-supported Blender E2E runner outside the sandbox:
  - `poetry run python scripts/run_e2e_tests.py`
  - result: `477 passed, 3 skipped`
- repo-wide quality gates:
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result: passed
- diff hygiene:
  - `git diff --check`
  - result: passed
