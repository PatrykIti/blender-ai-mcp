# TASK-142-01: Creature-Part Attachment Taxonomy and Truth Surface

**Parent:** [TASK-142](./TASK-142_Creature_Part_Seating_And_Organic_Attachment_Semantics.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. The repo now has one explicit
required creature seam taxonomy for guided assembled-creature scope and carries
that taxonomy into pair planning, truth payloads, and regression coverage
instead of relying only on primary-anchor pair expansion.

## Objective

Define one deterministic assembled-creature seam taxonomy and carry it into the
truth/correction surface so the guided loop can distinguish local overlap
cleanup from the full set of organic seating/attachment failures that still
matter on a squirrel-sized build.

## Business Problem

The current truth surface can already report `gap`, `overlap`,
`contact_failure`, and some attachment semantics, but the assembled creature
still fails as a whole because the loop does not yet carry the full required
seam set in one deterministic plan.

The missing layer is not just "one more attachment label." It is:

- which seams are required for a valid assembled squirrel stage
- how those seams are expanded from collection/object-set scope
- how multiple failing required seams stay visible together in truth-followup
  and candidate ranking

Without that coverage model, a run can improve one local pair while the rest of
the creature remains detached.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- the repo has one explicit deterministic taxonomy for the targeted creature
  relations:
  - `Ear_* -> Head`
  - `Eye_* -> Head`
  - `Snout -> Head`
  - `Nose -> Snout` or `Nose -> Head`
  - `Head -> Body`
  - `Tail -> Body`
  - `Forelimb_* -> Body`
  - `Hindlimb_* -> Body`
  - segmented limb relations when upper/lower limb masses stay separate
- truth/correction payloads can express when attachment semantics are still
  wrong even if raw overlap is zero
- collection/object-set scope can expand into the required creature seam set
  instead of only a narrow anchor-only pair list
- multiple failing required seams can stay visible together in loop-facing
  truth/correction output
- the attachment taxonomy is clearly separated from generic hard-surface
  contact semantics
- the same targeted relations drive both runtime behavior and regression scope

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`

## Changelog Impact

- include in the parent `TASK-142` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-142-01-01](./TASK-142-01-01_Organic_Attachment_Taxonomy_For_Head_Face_Torso_Tail_And_Limbs.md) | Define the targeted creature seam taxonomy, required pair list, and deterministic matching boundaries for an assembled squirrel-style build |
| 2 | [TASK-142-01-02](./TASK-142-01-02_Truth_Followup_And_Correction_Candidate_Attachment_Semantics.md) | Carry that taxonomy into multi-pair truth-followup and ranked correction-candidate semantics instead of a narrow anchor-only handoff |

## Status / Board Update

- keep board tracking on the parent `TASK-142`
- do not promote this subtask independently unless the attachment taxonomy
  needs its own review checkpoint
