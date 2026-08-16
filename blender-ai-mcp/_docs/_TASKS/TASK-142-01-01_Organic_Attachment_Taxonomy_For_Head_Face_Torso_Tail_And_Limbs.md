# TASK-142-01-01: Organic Attachment Taxonomy for Head, Face, Torso, Tail, and Limbs

**Parent:** [TASK-142-01](./TASK-142-01_Creature_Part_Attachment_Taxonomy_And_Truth_Surface.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Defined the first bounded
guided-creature seam taxonomy covering face/head, nose/snout, head/body,
tail/body, limb/body, and limb-segment relations with deterministic name-based
matching and explicit embedded vs seated vs segment attachment categories.

## Objective

Define one deterministic relation taxonomy for the targeted creature-part and
body-mass pairs so the repo can tell "generic overlap" apart from "organic
part is seated or attached incorrectly" across a whole assembled creature.

## Business Problem

The targeted squirrel failures were not just geometry glitches; they were
coverage-model glitches:

- the run needs a required seam list, not just a few ad hoc name hints
- ears should grow out of the head, not be treated like generic isolated parts
- eyes should sit against the head, not float after cleanup
- snout and nose should remain seated/attached, not be pushed away just
  because overlap went to zero
- the head should stay seated into the torso/body mass instead of reading as a
  detached floating piece
- the tail should stay attached to the body instead of drifting into a visibly
  disconnected relation
- limb masses should read as properly seated against the torso or their parent
  limb segment, not as generic detached appendages

This leaf owns the explicit relation vocabulary, required pair list, and
matching boundaries that the rest of `TASK-142` will build on.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the targeted creature pairs have explicit semantic categories such as:
  - overlap cleanup only
  - seated contact / attachment repair
  - embedded base-seating / emerge-from-surface repair
- the targeted relation list explicitly covers head/face attachments plus
  head-to-body, tail-to-body, and limb attachment seams
- the task defines which of those pairs are required seams for an assembled
  creature checkpoint versus optional or out-of-scope relations
- the taxonomy is deterministic and bounded to named creature-part relations,
  not a vague prompt-only heuristic
- the taxonomy is documented clearly enough that later truth/macro logic can
  use it without redefining the relations ad hoc

## Leaf Work Items

- define the targeted relation categories and their intended geometric outcome
- define the name/role-based matching rules and required seam list for the
  first supported creature pairs
- document explicit non-goals so generic hard-surface contact semantics do not
  get folded into this taxonomy accidentally

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- record the final targeted relation taxonomy and required seam list in the
  parent summary when this leaf closes
