# 379. TASK-178 structured-findings reporting propagation

Date: 2026-05-30

## Summary

Completed `TASK-178` with subtask `TASK-178-03`: the structured per-finding
compare evidence now propagates into the macro verification report, so a finding
that names a specific part drives a targeted inspect recommendation and counts
toward the follow-up signal — instead of the structured findings being carried on
the contract but ignored by the report.

## Changes

- `server/adapters/mcp/vision/reporting.py`: `_vision_recommendations_for_macro`
  now emits a high-priority `inspect_scene` recommendation naming the parts (and
  axis/direction when known) of any structured `findings` with a `target_label`,
  and includes `result.findings` in the `requires_followup` computation.

## Tests

- `tests/unit/adapters/mcp/test_vision_macro_reporting.py`: a result carrying a
  structured finding with `target_label="head"` produces a targeted
  `inspect_scene` recommendation mentioning the part and sets `requires_followup`
- `ruff` and `mypy` clean; full `tests/unit` green

## Status

This closes the `TASK-178` family: `TASK-178-01` (VisionFinding contract +
`findings` field, changelog 372), `TASK-178-02` (strict-mode schema + parser
coercion, changelog 372), and `TASK-178-03` (this propagation) are all complete.

## Research Basis

GPTEval3D (arXiv:2401.04092), SpatialRGPT (arXiv:2406.01584): per-part,
view/axis-bound findings are most useful when they drive the next deterministic
check. Re-measure on `tests/fixtures/vision_eval` before claiming gains.
