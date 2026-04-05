# TASK-128-02-04-01: Iterate-Stage Adoption and Prioritization Order

**Parent:** [TASK-128-02-04](./TASK-128-02-04_Iterate_Stage_Integration_Docs_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Define how silhouette outputs and typed `action_hints` are consumed in
`reference_iterate_stage_checkpoint(...)` without displacing truth-driven or
hybrid correction signals.

## Current Runtime Baseline

Current docs/runtime already prioritize `loop_disposition`,
`correction_candidates`, `truth_followup`, and `correction_focus`. This leaf is
about inserting silhouette outputs into that order without demoting existing
truth-driven escalation.

The leaf also needs to make one present-day boundary explicit while Slice B is
still open:

- current prompt/docs must not teach `shape_mismatches`,
  `proportion_mismatches`, or `next_corrections` as though they were already
  the canonical top-level iterate-stage fields
- until the new silhouette outputs actually ship, current docs should describe
  those lists where they really live today:
  - `vision_assistant.result`
  - candidate-level vision evidence

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the prioritization order is explicit and stable
- truth-driven findings still outrank purely perceptual hints when appropriate
- docs show the intended operator/model reading order
- the leaf explicitly distinguishes:
  - the current pre-Slice-B iterate-stage reading order used by runtime/docs now
  - the future post-Slice-B insertion point for silhouette outputs and typed
    `action_hints`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
