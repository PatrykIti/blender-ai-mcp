# TASK-142-02-01: Overlap Cleanup vs Attachment Macro Selection Policy

**Parent:** [TASK-142-02](./TASK-142-02_Bounded_Macro_Selection_And_Repair_Behavior_For_Organic_Seating.md)
**Depends On:** [TASK-142-01-02](./TASK-142-01-02_Truth_Followup_And_Correction_Candidate_Attachment_Semantics.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Implemented deterministic
macro-family selection for the guided creature seam taxonomy so overlap
presence alone no longer forces `macro_cleanup_part_intersections` on organic
attachment cases that need re-seating.

## Objective

Define one deterministic policy for choosing cleanup, contact-repair, or
attach-to-surface macros on the targeted creature-part relations in a full
assembled-creature run.

## Business Problem

The current bounded repair path is still too overlap-centric. That makes it
easy for the loop to choose a technically-valid but semantically-wrong move:

- cleanup when the part should really be re-seated
- contact nudge when the relation really needs surface seating
- attachment framing missing entirely from the macro-candidate story
- one chosen macro family overshadowing other failing required seams in the same
  assembled creature

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- targeted creature-part pairs follow one deterministic macro-family decision
  policy
- overlap presence alone is no longer enough to force
  `macro_cleanup_part_intersections` on attachment/seating cases
- macro candidates and ranked correction candidates expose the selected repair
  family clearly enough for the operator to act without rediscovering policy
- multi-pair handoff can surface more than one required seam without collapsing
  everything into the first overlap-driven macro suggestion

## Leaf Work Items

- define the first-pass selection rules for cleanup vs contact repair vs
  attach/seat macros
- implement the chosen selection policy in truth-followup/correction-candidate
  generation
- add focused regression coverage for the targeted squirrel failure shapes,
  including assembled-creature multi-pair cases

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- record the shipped macro-selection policy and its multi-pair seam behavior in
  the parent summary when this leaf closes
