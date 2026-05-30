# 381. TASK-180-04 mark-keyed findings and correspondence table

Date: 2026-05-30

## Summary

Implemented the server-side core of `TASK-180-04`: structured findings can now be
keyed to a Set-of-Mark id, and a deterministic resolver maps those mark-keyed
findings back to the scene objects they label — with a validity guard that drops
references to marks that do not exist on the overlay (the VLM-Grounder check).

## Changes

- `server/adapters/mcp/sampling/result_types.py`: added `mark_id: int | None` to
  `VisionFindingContract` (the numbered overlay mark the model keyed the finding
  to; resolved server-side back to the scene object).
- `server/adapters/mcp/vision/parsing.py`: `_coerce_findings_list` now coerces
  `mark_id` (non-int -> None).
- `server/adapters/mcp/vision/marks.py`: added
  `build_mark_correspondence_table(findings, mark_id_to_object)` returning
  `(rows, validity_warnings)` — each row maps a finding's `mark_id` to its object;
  findings referencing a non-existent mark are dropped and recorded as a validity
  warning; findings with no `mark_id` flow through the normal channel.

## Tests

- `tests/unit/adapters/mcp/test_vision_marks.py`: the correspondence table
  resolves valid marks in order, drops a non-existent mark with one validity
  warning, and ignores mark-less findings
- `tests/unit/adapters/mcp/test_vision_parsing.py`: `mark_id` coercion (int kept,
  non-int -> None)
- `ruff`/`mypy` clean; full `tests/unit` green

## Follow-on (addon + E2E)

`TASK-180-02` (stable cross-view/iteration mark ids keyed to the live part
registry) and `TASK-180-03` (reference-image marks via the default-off
Grounded-SAM sidecar) remain open, plus wiring the overlay + correspondence table
into the live compare flow, which needs the `run_e2e_tests.py` cycle.

## Research Basis

VLM-Grounder (arXiv:2410.13860) validity retry against non-existent marks;
Set-of-Mark (arXiv:2310.11441). Re-measure on `tests/fixtures/vision_eval`.
