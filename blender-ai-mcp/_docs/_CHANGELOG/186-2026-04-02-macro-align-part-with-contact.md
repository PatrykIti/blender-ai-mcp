# 186. Macro align part with contact

Date: 2026-04-02

## Summary

Completed the second creature-correction macro leaf by adding
`macro_align_part_with_contact` as a bounded repair tool for already-related
pairs that almost fit.

## What Changed

- added `macro_align_part_with_contact` to the scene MCP surface
- implemented it as a truth-driven repair macro that:
  - reads current pair truth
  - infers a repair axis when possible
  - preserves the current side by default
  - enforces `max_nudge`
  - returns before/after truth summary in the macro report
- exposed the macro as a `truth_followup.macro_candidates` recommendation
  without enabling auto-apply in the loop
- added unit coverage for:
  - handler behavior
  - MCP wrapper behavior
  - structured delivery
  - provider inventory / guided visibility
  - truth-followup macro-candidate exposure
- added Blender-backed E2E coverage for the repair macro

## Why

The repo already had bounded initial placement tools, but not a safe repair
tool for pairs that were already close to correct. This macro closes that gap
without collapsing into a broader re-placement or auto-apply loop.
