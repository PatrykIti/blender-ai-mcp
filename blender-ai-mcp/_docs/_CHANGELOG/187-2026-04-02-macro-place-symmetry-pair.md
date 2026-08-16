# 187. Macro place symmetry pair

Date: 2026-04-02

## Summary

Completed the third creature-correction macro leaf by adding
`macro_place_symmetry_pair` as a bounded mirrored-pair placement/correction
tool.

## What Changed

- added `macro_place_symmetry_pair` to the scene MCP surface
- implemented it as a bounded pair-level symmetry macro that:
  - chooses an anchor object (`left`, `right`, or `auto`)
  - mirrors the follower object's center across an explicit mirror plane
  - verifies the result with `scene_assert_symmetry`
- exposed structured delivery, provider inventory, compatibility policy, and
  guided build-surface visibility for the new macro
- added coverage for:
  - macro handler behavior
  - MCP wrapper behavior
  - structured delivery
  - provider inventory / guided surface visibility
  - Blender-backed E2E symmetry-pair placement

## Why

The macro wave needed one pair-level symmetry tool distinct from both generic
layout and pair repair. This closes the gap for mirrored ears/eyes/limbs
without introducing free-form mirroring or broader geometry-side symmetry work.
