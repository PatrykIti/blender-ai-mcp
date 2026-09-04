# 192. Correction candidate contract and priority model

Date: 2026-04-02

## Summary

Completed the first hybrid-loop leaf by adding a ranked `correction_candidates`
contract for stage compare and iterate responses.

## What Changed

- added a merged `correction_candidates` field to
  `ReferenceCompareStageCheckpointResponseContract` and
  `ReferenceIterateStageCheckpointResponseContract`
- defined one explicit candidate shape that can carry:
  - ranked correction priority
  - vision evidence
  - truth evidence
  - bounded macro options
- implemented candidate building so:
  - truth-driven pair findings become ranked `truth_only` candidates
  - matching vision focus can upgrade them into `hybrid` candidates
  - unmatched vision focus items remain ranked `vision_only` candidates
- preserved source boundaries instead of flattening vision/truth/macro signals
  into one opaque score
- added unit coverage for:
  - candidate construction and hybrid merge behavior
  - stage-compare response population
  - iterate response carry-through

## Why

The hybrid-loop subtree needed one explicit handoff contract before later work
can safely change truth integration and loop-disposition policy. Without this,
priority still depends on ad hoc prose order across separate `correction_focus`,
`truth_followup`, and `macro_candidates` payloads.
