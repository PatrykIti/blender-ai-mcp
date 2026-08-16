# 171. Session-aware reference auto loop

Date: 2026-03-30

## Summary

Added the first session-aware auto-loop controller for reference-guided staged
building.

## What Changed

- added `reference_iterate_stage_checkpoint(...)`
- the new tool:
  - captures deterministic stage views
  - compares them against attached references
  - remembers the prior `correction_focus`
  - returns `loop_disposition`:
    - `continue_build`
    - `inspect_validate`
    - `stop`
- repeated focus across iterations now escalates into `inspect_validate`
  instead of asking the model to keep free-form guessing
- updated prompt/docs so reference-guided creature workflows can use the new
  iterate tool as the default staged loop entrypoint

## Why

The repo already had bounded compare surfaces, but the loop was still
stateless. The model had to remember whether it was seeing the same correction
again. This change moves that minimal loop memory into the product surface.
