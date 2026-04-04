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

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the prioritization order is explicit and stable
- truth-driven findings still outrank purely perceptual hints when appropriate
- docs show the intended operator/model reading order

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
