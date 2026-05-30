# 373. TASK-182 stable defect-id substrate for Critic/Verify

Date: 2026-05-30

## Summary

Implemented the foundational substrate for `TASK-182` (subtask `TASK-182-01`):
each structured compare finding now carries a server-computed, stable
`defect_id`, so a Critic finding can be tracked and checked off by a later
Verify pass instead of being re-described every cycle. This is the identity layer
the Critic/Verify loop and the deterministic-first exit criteria build on.

## Changes

- `server/adapters/mcp/sampling/result_types.py`: added `defect_id: str | None`
  to `VisionFindingContract` (server-computed, not part of the response schema so
  the model cannot perturb it).
- `server/adapters/mcp/vision/parsing.py`: `_coerce_findings_list` now derives a
  deterministic `defect_id` from a stable key (canonical target label, axis,
  direction, and a whitespace/case-normalized text key), hashed with SHA-1 and
  truncated. Re-phrasings of the same defect collide to the same id; a different
  target/axis yields a different id.

## Tests

- `tests/unit/adapters/mcp/test_vision_parsing.py`: defect ids are stable across
  case/whitespace variants of the same finding and differ across targets
- `ruff` and `mypy` clean on the touched modules

## Follow-on

The full `TASK-182` Critic/Verify loop (re-render the same views and check off
each open `defect_id`) and the deterministic-first layered exit with consolidated
`authoritative_next_actions` (`TASK-182-02`) remain open; they touch the staged
compare orchestration and warrant a dedicated implementation + E2E pass.

## Research Basis

LL3M (arXiv:2508.08228): a Critic/Verification split that re-checks each prior
defect after an edit. Re-measure on `tests/fixtures/vision_eval` before claiming
gains.
