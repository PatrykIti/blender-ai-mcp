# Hybrid Loop Real Creature Eval

This document defines the current practical regression pack for the hybrid
assembled-creature correction loop introduced under `TASK-122`.

Its purpose is simple:

- keep one explicit list of real or Blender-backed creature scenarios
- state which output fields matter for each scenario
- make later regressions measurable without reinventing the eval plan every time

## Scenario Pack

### 1. Blender-backed Truth Handoff

File:
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

Purpose:
- prove that staged compare responses expose:
  - `truth_bundle`
  - `truth_followup`
  - `correction_candidates`

Expected signal:
- pairwise truth findings exist for an assembled creature-style object set
- `truth_followup.focus_pairs` names the problematic pair
- `correction_candidates` preserve truth provenance instead of flattening it

This is the first line of defense for hybrid-loop payload regressions.

### 2. Real Reference-Guided Creature Comparison

File:
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`

Purpose:
- validate that a real vision backend still returns bounded creature guidance
  on repo-tracked squirrel checkpoint images plus user-supplied front/side
  references

Required environment:
- `RUN_REAL_REFERENCE_GUIDED_CREATURE_EVAL=1`
- `VISION_REFERENCE_FRONT_PATH`
- `VISION_REFERENCE_SIDE_PATH`
- optional `VISION_REFERENCE_CREATURE_MODEL`

Expected signal:
- `reference_match_summary`
- bounded mismatch lists
- bounded `correction_focus`
- bounded `next_corrections`

This is the first line of defense for real-model output drift on creature
reference comparison.

## Output Review Order

For hybrid-loop regression review, inspect result fields in this order:

1. `loop_disposition`
2. `correction_candidates`
3. `truth_followup`
4. `correction_focus`
5. `shape_mismatches` / `proportion_mismatches`
6. `next_corrections`

Why this order:

- `loop_disposition` decides whether free-form building should continue at all
- `correction_candidates` are the ranked merged handoff across vision, truth,
  and bounded macros
- `truth_followup` preserves the raw deterministic truth findings behind that
  ranking
- `correction_focus` remains the compact loop-facing summary
- the remaining vision lists are still useful, but lower level than the merged
  hybrid handoff

## Practical Failure Modes To Watch

Treat these as regression signals:

- `truth_bundle` disappears from staged compare / iterate responses
- `truth_followup` exists but loses focus pairs or macro candidates
- `correction_candidates` stop preserving source boundaries
- truth-heavy issues no longer escalate `loop_disposition` to
  `inspect_validate`
- real creature comparison returns unbounded list spam or empty correction
  guidance without a credible alignment summary

## Prompting Guidance Link

Use this document together with:

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

That prompt guide defines how an operator or client prompt should consume the
hybrid loop outputs during staged creature work.
