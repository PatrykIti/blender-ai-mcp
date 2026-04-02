# 193. Iterate stage truth bundle integration

Date: 2026-04-02

## Summary

Completed the second hybrid-loop leaf by wiring truth-integrated ranked
`correction_candidates` into `reference_iterate_stage_checkpoint(...)`.

## What Changed

- updated `reference_iterate_stage_checkpoint(...)` so loop-facing
  `correction_focus` now prefers ranked `correction_candidates` summaries when
  they are present
- this lets the staged loop surface:
  - truth-only issues
  - hybrid truth + vision issues
  - bounded macro options already attached to those candidates
- kept source boundaries intact by leaving the full `correction_candidates`,
  `truth_followup`, and `truth_bundle` payloads on the response contract
- added unit coverage for:
  - truth-only candidate fallback into iterate `correction_focus`
  - existing vision-driven iterate behavior remaining intact

## Why

The staged correction loop needed to actually consume truth-integrated hybrid
payloads, not just carry them through as unused fields. This leaf gives the
loop a bounded way to see deterministic spatial evidence alongside vision
output before the later disposition-policy leaf changes how stop/continue
decisions are computed.
