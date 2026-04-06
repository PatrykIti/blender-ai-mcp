# TASK-142-01: Creature-Part Attachment Taxonomy and Truth Surface

**Parent:** [TASK-142](./TASK-142_Creature_Part_Seating_And_Organic_Attachment_Semantics.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one deterministic creature-part attachment taxonomy and carry it into
the truth/correction surface so the guided loop can distinguish overlap cleanup
from organic seating/attachment failures.

## Business Problem

The current truth surface can report `gap`, `overlap`, and `contact_failure`,
but it still lacks the semantic layer that matters for organic creature parts:

- some pairs are supposed to be merely separated
- some pairs are supposed to stay in seated contact
- some pairs are supposed to emerge from another mass without floating or
  visibly growing through the surface

Without that taxonomy, overlap removal can look like success even when the
attachment semantics are still wrong.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
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

## Changelog Impact

- include in the parent `TASK-142` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-142-01-01](./TASK-142-01-01_Organic_Attachment_Taxonomy_For_Head_Face_Torso_Tail_And_Limbs.md) | Define the targeted creature-part relation taxonomy and deterministic boundaries |
| 2 | [TASK-142-01-02](./TASK-142-01-02_Truth_Followup_And_Correction_Candidate_Attachment_Semantics.md) | Carry that taxonomy into truth-followup and ranked correction-candidate semantics |

## Status / Board Update

- keep board tracking on the parent `TASK-142`
- do not promote this subtask independently unless the attachment taxonomy
  needs its own review checkpoint
