# 190. Macro place supported pair

Date: 2026-04-02

## Summary

Completed the sixth creature-correction macro leaf by adding
`macro_place_supported_pair` as a bounded mirrored-pair placement tool against
one shared support surface.

## What Changed

- added `macro_place_supported_pair` to the scene MCP surface
- implemented it as a bounded macro that:
  - takes one existing left/right pair plus one existing support object
  - keeps symmetry and support contact as separate explicit constraints
  - preserves one anchor object (`left`, `right`, or `auto`)
  - blocks when support placement would require materially different support
    coordinates and would therefore break the bounded mirrored pair
- exposed structured delivery, provider inventory, compatibility policy, and
  guided build-surface visibility for the new macro
- generalized the original limb-centric planning name immediately so the public
  tool also fits non-body cases such as chair legs or landing skids
- added coverage for:
  - macro handler behavior
  - MCP wrapper behavior
  - structured delivery
  - provider inventory / guided surface visibility
  - Blender-backed E2E supported-pair placement

## Why

The macro wave needed one bounded way to keep a mirrored pair aligned while
also seating both objects onto the same support surface, without drifting into
rigging, pose mode, or open-ended manual transform chaining.
