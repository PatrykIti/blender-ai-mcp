# 198. Hybrid loop model-aware budget and scope control

Date: 2026-04-03

## Summary

Closed the hybrid-loop budget/scope follow-on by adding model-aware trimming
for truth and correction-candidate payloads on staged compare flows.

## What Changed

- stage compare now derives a bounded pair budget from:
  - active runtime output-token limits
  - active image budget
  - a small deterministic model-name bias
- truth bundles are trimmed to the highest-value pair checks when needed
- ranked correction candidates are trimmed to a bounded count when needed
- compare and iterate responses now expose `budget_control` so clients can see:
  - original vs emitted pair counts
  - original vs emitted candidate counts
  - whether trimming was applied
  - which focus pairs survived trimming
- existing behavior remains unchanged for smaller scopes that already fit the
  runtime budget

## Why

Large assembled collections were still able to hit `input_budget_exceeded`
because truth and candidate payloads expanded with one static shape. This
follow-on makes the hybrid loop degrade gracefully instead of failing late.
