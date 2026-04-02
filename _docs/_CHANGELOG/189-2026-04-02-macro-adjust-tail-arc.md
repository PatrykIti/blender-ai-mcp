# 189. Macro adjust tail arc

Date: 2026-04-02

## Summary

Completed the fifth creature-correction macro leaf by adding
`macro_adjust_tail_arc` as a bounded chain-arc adjustment tool for segmented
tail objects.

## What Changed

- added `macro_adjust_tail_arc` to the scene MCP surface
- implemented it as a bounded macro that:
  - takes an ordered chain of existing segment objects
  - keeps the first segment anchored
  - places the remaining segments along a planar arc
  - optionally applies progressive rotation around one explicit rotation axis
- exposed structured delivery, provider inventory, compatibility policy, and
  guided build-surface visibility for the new macro
- added coverage for:
  - macro handler behavior
  - MCP wrapper behavior
  - structured delivery
  - provider inventory / guided surface visibility
  - Blender-backed E2E tail-chain arc adjustment

## Why

The macro wave needed one bounded way to reshape segmented tails without
dropping into free-form manual transform chains, rigging, or curve deformation.
