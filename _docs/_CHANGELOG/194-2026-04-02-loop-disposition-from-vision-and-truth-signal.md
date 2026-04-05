# 194. Loop disposition from vision and truth signal

Date: 2026-04-02

## Summary

Completed the third hybrid-loop leaf by letting
`reference_iterate_stage_checkpoint(...)` escalate `loop_disposition` from both
vision-derived focus and deterministic truth evidence.

## What Changed

- kept the existing bounded actionability / repeated-focus loop behavior
- added a deterministic truth-driven escalation rule:
  - if ranked `correction_candidates` contain high-priority truth evidence
    such as `contact_failure`, `overlap`, or `measurement_error`
  - then `loop_disposition` becomes `inspect_validate`
- kept provenance intact by deriving that decision from the ranked candidate
  payload instead of flattening truth into a fuzzy confidence score
- added unit coverage for:
  - truth-driven inspect escalation
  - existing continue-build behavior remaining intact

## Why

The hybrid loop needed a bounded path from “vision says keep iterating” to
“deterministic truth says stop and verify first.” This change adds that policy
without collapsing into open-ended model judgment.
