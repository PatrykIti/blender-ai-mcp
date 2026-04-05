# 183. Correction truth bundle baseline

Date: 2026-04-01

## Summary

Completed the second `TASK-122` truth leaf by adding a correction-oriented
truth bundle for assembled-model stage compare and iterate flows.

## What Changed

- added a structured `truth_bundle` for stage compare and iterate responses
- the bundle now groups existing deterministic findings per assembled-target
  pair:
  - contact assertion
  - measured gap
  - measured alignment
  - measured overlap
- added summary-level counters for:
  - pairing strategy
  - evaluated pairs
  - contact failures
  - overlap pairs
  - separated pairs
  - misaligned pairs
- passed the bundle into the vision request as deterministic `truth_summary`
  context so the vision layer can interpret visible change with the current
  geometric state in view

## Why

The hybrid correction loop needs one correction-ready truth carrier instead of
isolated raw measure/assert results. This bundle is the first reusable baseline
for that later handoff.
