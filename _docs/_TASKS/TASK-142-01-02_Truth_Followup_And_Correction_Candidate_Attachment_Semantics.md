# TASK-142-01-02: Truth-Followup and Correction-Candidate Attachment Semantics

**Parent:** [TASK-142-01](./TASK-142-01_Creature_Part_Attachment_Taxonomy_And_Truth_Surface.md)
**Depends On:** [TASK-142-01-01](./TASK-142-01-01_Organic_Attachment_Taxonomy_For_Head_Face_Torso_Tail_And_Limbs.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Carry the organic attachment taxonomy into `truth_followup` and
`correction_candidates` so the guided loop can express "attachment semantics
still wrong" as first-class evidence.

## Business Problem

Right now the truth surface mostly says:

- overlap
- gap
- contact failure
- alignment issue

That is not enough for the creature-part cases that motivated `TASK-142`,
because the operator still needs to know whether a pair is:

- floating
- intersecting
- or attached in the wrong way for this organic relation

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- truth-followup can surface attachment-semantics evidence for the targeted
  creature-part relations
- ranked correction candidates can carry that same evidence through the hybrid
  loop instead of flattening it to generic gap/overlap wording
- the loop can distinguish "overlap removed" from "attachment repaired"
  without relying only on prose interpretation

## Leaf Work Items

- extend the truth/correction surface with the needed attachment-semantics
  payload shape
- align candidate summaries, priorities, and evidence kinds with the new
  relation taxonomy
- add focused contract-level regression coverage

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- update the parent summary so it explicitly calls out the shipped
  truth-surface attachment semantics when this leaf closes
