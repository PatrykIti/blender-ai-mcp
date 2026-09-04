# 191. Macro cleanup part intersections

Date: 2026-04-02

## Summary

Completed the seventh creature-correction macro leaf by adding
`macro_cleanup_part_intersections` as a bounded overlap-cleanup tool for one
existing object pair.

## What Changed

- added `macro_cleanup_part_intersections` to the scene MCP surface
- implemented it as a bounded macro that:
  - reads overlap truth before moving anything
  - infers a stable cleanup axis from the current overlap footprint
  - preserves the current side when possible
  - pushes one object out to contact or a small gap
  - blocks when the required cleanup push exceeds `max_push`
- exposed structured delivery, provider inventory, compatibility policy, and
  guided build-surface visibility for the new macro
- extended `truth_followup.macro_candidates` so overlap-driven pair issues can
  recommend `macro_cleanup_part_intersections`
- added coverage for:
  - macro handler behavior
  - MCP wrapper behavior
  - structured delivery
  - provider inventory / guided surface visibility
  - truth-followup overlap candidate exposure
  - Blender-backed E2E overlap cleanup

## Why

The macro wave still lacked one bounded way to turn obvious pairwise clipping
or penetration into a deterministic corrective move. This closes the macro
subtree with a narrow overlap-cleanup tool instead of relying on ad hoc manual
transforms or free-form collision solving.
