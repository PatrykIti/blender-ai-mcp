# 201. Cross-domain refinement routing regression pack

Date: 2026-04-03

## Summary

Closed the final leaf of the cross-domain refinement-routing follow-on by
formalizing the regression pack and prompting guidance for `refinement_route`
and `refinement_handoff`.

## What Changed

- added `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- documented expected routing across:
  - hard-surface / electronics
  - building / architecture
  - garments / soft accessories
  - organs / anatomy
  - creatures / characters
  - low-poly assembled models
- updated prompt/docs guidance so operators review outputs in the order:
  - `loop_disposition`
  - `refinement_route`
  - `refinement_handoff`
  - `correction_candidates`
  - `truth_followup`
  - `correction_focus`

## Why

The routing selector and sculpt handoff were already implemented, but the repo
still needed one explicit cross-domain regression story so later policy changes
can be judged on more than a single squirrel scenario.
