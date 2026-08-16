# 195. Real assembled creature eval and prompting

Date: 2026-04-02

## Summary

Completed the final hybrid-loop leaf by formalizing the real assembled-creature
regression pack and updating prompt guidance for the new hybrid loop outputs.

## What Changed

- added `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md` as the explicit
  regression pack for the hybrid assembled-creature loop
- documented which real or Blender-backed scenarios currently validate:
  - truth handoff
  - ranked correction candidates
  - real creature comparison output
- updated prompt guidance so staged creature work now consumes hybrid loop
  output in this order:
  - `loop_disposition`
  - `correction_candidates`
  - `truth_followup`
  - `correction_focus`
- updated test/docs guidance to point at the same regression pack instead of
  leaving the eval story split across unrelated notes

## Why

The runtime subtree was already in place, but the repo still needed one clear
answer to “which creature scenarios validate the hybrid loop now, and how
should prompts consume its outputs?” This closes that gap and makes later
regressions easier to measure repeatably.
