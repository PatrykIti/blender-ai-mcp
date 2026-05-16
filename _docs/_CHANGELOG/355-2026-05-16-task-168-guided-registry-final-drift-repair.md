# 355. TASK-168 guided registry final drift repair

Date: 2026-05-16

## Summary

Closed the final `TASK-168` guided-registry drift found by the post-commit
agent pass after the compact-boundary repair.

The repair pass:

- made `guided_register_part(...)` fail closed through the typed router status
  and `reference_orchestrator_feedback` surface when no valid active guided flow
  exists, instead of allowing a registry-owner `ValueError` to escape
- kept successful scene identity mutations synchronized with the guided part
  registry even when a later corrected step fails closed
- let corrected create-then-transform sequences validate each step against the
  latest guided session state, so the transform can use the role registered by
  the preceding create step
- ensured async public modeling wrappers finalize partial failed route reports
  before returning legacy text, preserving stale-state and registry finalizers
  for successful steps inside failed corrected reports
- made router goal/status/clear paths prefer the running FastMCP surface profile
  over stale config/session values, preserving the runtime-authority contract
  for factory-built `llm-guided` servers
- cleared stale fail-closed router feedback after a successful
  `guided_register_part(...)` retry, so status no longer projects an old
  registration block
- routed successful async modeling create/transform reports through the central
  async finalizer too, so corrected multi-step successes keep complete
  dirty-scope/identity finalization
- added active compare-scope coverage for `last_mutation`, `active_workset`,
  and omitted-target staged compare fallback paths
- refreshed TASK-168 closeout docs so completed umbrella/child tasks record the
  actual final unit, pre-commit, and Blender E2E proof instead of stale
  docs-only/future-tense wording

## Validation

- targeted owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
  - result: `108 passed`
- post-agent targeted owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_reference_images.py -q`
  - result: `192 passed`
- docs-only post-pass validation:
  - `git diff --check`
  - targeted stale-disclosure and closeout consistency greps
- broad repo unit proof outside the sandbox:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - result: `3457 passed`
- repo-supported Blender E2E runner outside the sandbox:
  - `poetry run python scripts/run_e2e_tests.py`
  - result: `477 passed, 3 skipped`
- repo-wide quality gates:
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result: passed
- diff hygiene:
  - `git diff --check`
  - result: passed
