# TASK-142-01-02: Truth-Followup and Correction-Candidate Attachment Semantics

**Parent:** [TASK-142-01](./TASK-142-01_Creature_Part_Attachment_Taxonomy_And_Truth_Surface.md)
**Depends On:** [TASK-142-01-01](./TASK-142-01-01_Organic_Attachment_Taxonomy_For_Head_Face_Torso_Tail_And_Limbs.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Carry the organic attachment taxonomy into `truth_followup` and
`correction_candidates` so the guided loop can express "attachment semantics
still wrong" as first-class evidence across multiple required creature seams in
the same assembled-model run.

## Business Problem

Right now the truth surface mostly says:

- overlap
- gap
- contact failure
- alignment issue

That is not enough for the creature-part cases that motivated `TASK-142`,
because the operator still needs to know:

- which required creature seams are currently failing
- whether a pair is floating, intersecting, or attached in the wrong way
- how those multiple failing seams should be prioritized in one loop handoff

Without that multi-pair carry-through, a run can fix one local seam and still
leave the rest of the squirrel disconnected.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- truth-followup can surface attachment-semantics evidence for the targeted
  creature-part relations
- ranked correction candidates can carry that same evidence through the hybrid
  loop instead of flattening it to generic gap/overlap wording
- the loop can distinguish "overlap removed" from "attachment repaired"
  without relying only on prose interpretation
- multi-pair collection/object-set checkpoints can emit more than one failing
  required seam with deterministic focus order
- correction candidates preserve which failing seams are still unresolved after
  another seam has already improved

## Leaf Work Items

- extend the truth/correction surface with the needed attachment-semantics
  payload shape
- align candidate summaries, priorities, and evidence kinds with the new
  relation taxonomy
- extend the truth handoff beyond a narrow primary-target-only view where
  required creature seams would otherwise disappear
- add focused contract-level plus assembled-creature truth regressions

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- update the parent summary so it explicitly calls out the shipped multi-pair
  truth-surface attachment semantics when this leaf closes
