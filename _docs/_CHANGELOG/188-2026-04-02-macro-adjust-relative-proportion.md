# 188. Macro adjust relative proportion

Date: 2026-04-02

## Summary

Completed the fourth creature-correction macro leaf by adding
`macro_adjust_relative_proportion` as a bounded ratio-repair tool for related
objects.

## What Changed

- added `macro_adjust_relative_proportion` to the scene MCP surface
- implemented it as a bounded proportion-repair macro that:
  - reads the current cross-object ratio through `scene_assert_proportion`
  - scales one explicit target object (`primary` or `reference`)
  - enforces `max_scale_delta`
  - re-checks the result after the scale repair
- exposed structured delivery, provider inventory, compatibility policy, and
  guided build-surface visibility for the new macro
- added coverage for:
  - macro handler behavior
  - MCP wrapper behavior
  - structured delivery
  - provider inventory / guided surface visibility
  - Blender-backed E2E proportion repair

## Why

The macro wave needed one bounded tool for obvious cross-object size drift. This
closes that gap without turning the flow into open-ended scaling or sculpting.
