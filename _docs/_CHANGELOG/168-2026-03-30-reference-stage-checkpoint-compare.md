# 168. Reference stage checkpoint compare

Date: 2026-03-30

## Summary

Added a deterministic multi-view stage checkpoint compare surface for
reference-guided manual builds.

## What Changed

- added `reference_compare_stage_checkpoint(...)` to the public reference
  surface
- reused the shared `compact` / `rich` capture preset profiles so staged manual
  work can capture a repeatable front/side/top-oriented checkpoint set without
  a full macro/workflow bundle
- the new surface now returns both:
  - bounded `vision_assistant` interpretation
  - the capture artifacts used for the comparison
- updated guided visibility/discovery so the new surface is available on
  manual build/inspect flows

## Why

`reference_compare_current_view(...)` was useful for one-off checkpoint checks,
but staged creature/reference work still needed a stronger deterministic path
than a single ad hoc viewport shot. This adds the first proper multi-view stage
checkpoint path that can be reused inside later iterative correction loops.
