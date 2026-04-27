# 223. Qwen 32B operator compare note

Date: 2026-04-07

## Summary

Updated the external vision provider notes to reflect a new operator-reported
success for `qwen/qwen3-vl-32b-instruct` on
`reference_compare_current_view(...)`, while keeping the model off the default
recommendation path until stronger reproduced evidence exists.

## What Changed

- updated the `qwen/qwen3-vl-32b-instruct` row in `_docs/_VISION/README.md`
  from a pure weak-smoke note to mixed evidence:
  - older weak `macro_finish_form` smoke remains recorded
  - one `2026-04-07` operator-reported squirrel
    `reference_compare_current_view(...)` success is now recorded
- clarified that operator-reported rows can capture both success and
  instability without counting as promotion-grade evidence
- recorded the current quality caveat from the operator report:
  structured payload succeeded, but one `next_corrections` item was truncated

## Validation

- docs-only change
- no code or test changes were required

## Why

The branch evidence had drifted: repo docs still described
`qwen/qwen3-vl-32b-instruct` only as a weak smoke datapoint even after a real
guided compare run returned the expected structured payload. The docs now match
the current evidence without overstating model reliability.
