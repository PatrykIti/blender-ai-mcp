# 200. Guided surface sculpt handoff

Date: 2026-04-03

## Summary

Implemented the first guided-surface sculpt policy shape as a
recommendation-only handoff instead of a visibility unlock.

## What Changed

- hybrid compare/iterate responses now expose `refinement_handoff`
- when `refinement_route.selected_family == "sculpt_region"`, the handoff can
  recommend a bounded deterministic sculpt subset:
  - `sculpt_deform_region`
  - `sculpt_smooth_region`
  - `sculpt_inflate_region`
  - `sculpt_pinch_region`
- the normal `llm-guided` build visibility remains unchanged:
  sculpt is still hidden by default
- unit coverage now validates sculpt handoff recommendation without requiring a
  visibility unlock

## Why

The product needed a safer midpoint between “never mention sculpt” and “show
all sculpt tools.” Recommendation-only handoff gives the loop a deterministic
way to suggest sculpt without reopening the guided surface too broadly.
