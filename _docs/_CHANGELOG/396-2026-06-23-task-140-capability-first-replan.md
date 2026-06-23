# 396. TASK-140 capability-first replan

Date: 2026-06-23

Closed `TASK-140` as a docs/task-governance reconciliation with the shipped
capability-aware OpenRouter runtime.

## Changed

- Reframed `TASK-140` from broad model-family `vision_contract_profile`
  expansion to a capability-first closeout.
- Closed `TASK-140-06`, `TASK-140-06-02`, and `TASK-140-06-04` against the
  already-shipped OpenRouter metadata, fallback capability, request-policy,
  diagnostics, result-contract, and harness surfaces.
- Marked the old `TASK-140-01` through `TASK-140-05` family-profile hierarchy
  as superseded.
- Added `TASK-187` as the standalone follow-up for evidence-backed external
  model fallback/profile promotion.
- Updated task board, vision docs, MCP server docs, and the reference
  understanding roadmap to describe the current capability-first direction.

## Validation

- Docs/process validation only; no runtime code changed.
- `git diff --check`
- `TASK-140` open-descendant consistency grep returned no open descendants.
- Board count audit matched promoted rows:
  `To Do: 6`, `In Progress: 2`, `Done: 116`.
- Changelog index audit found entry `396`.
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  passed.
