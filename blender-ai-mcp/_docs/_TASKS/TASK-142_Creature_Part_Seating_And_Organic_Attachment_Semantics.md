# TASK-142: Creature Part Seating and Organic Attachment Semantics

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Product Reliability / Organic Part Placement
**Follow-on After:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)

**Completion Summary:** Completed on 2026-04-07. The guided assembled-creature
truth path now expands supported collection/object-set scopes into one
deterministic required seam set for face/head, nose/snout, head/body,
tail/body, and limb attachments; carries structured attachment semantics and
attachment verdicts through `truth_bundle`, `truth_followup`, and
`correction_candidates`; selects bounded macro families by seam type instead of
reusing overlap cleanup by default; and ships focused unit/docs plus
Blender-backed assembled-creature E2E coverage for the squirrel-style failure
mode that motivated this follow-on.

## Objective

Make the guided creature correction path evaluate and repair the full assembled
creature seam set, so head, face, torso, tail, and limb masses stop passing as
"good enough" while still floating apart from the body.

## Business Problem

The repo now has attachment-aware wording, macro candidates, and
`attachment_verdict` semantics, but the latest real squirrel runs still finish
with most major parts visibly detached from the body.

The core gap is no longer "there is no attachment vocabulary at all." The core
gap is that the assembled-creature truth/correction path still does not cover
or prioritize enough of the required seam set in one run.

Observed failure shapes:

- ears can be repaired locally while the rest of the creature still remains
  disconnected
- eyes, snout, and nose can still float away from the head after the run moves
  on to later stages
- head/body, tail/body, and upper/lower limb seams can remain visibly detached
  even though the session no longer reports an urgent geometry problem
- collection/object-set stage checks still bias too much toward one primary
  anchor path, so important creature seams are not all surfaced together
- bounded macro outcomes can still look locally acceptable while the assembled
  creature is globally wrong because multiple required attachment pairs were
  never elevated into the correction loop

This is not the same as the `TASK-141` contract problem. `TASK-141` is about
reaching the right surface. `TASK-142` is about making the full assembled
creature truth/repair path prove and fix the right relations once the session
is already on that surface.

## Scope

This follow-on covers:

- defining the required assembled-creature seam set and making it visible to the
  truth/correction loop in one run
- clarifying which targeted creature-part relations are:
  - overlap cleanup only
  - attachment/seating/contact repair
  - embedded or segment-style attachment that must stay seated into the anchor
    mass
- improving bounded repair guidance and prioritization for:
  - `Ear_* -> Head`
  - `Eye_* -> Head`
  - `Snout -> Head`
  - `Nose -> Snout` or `Nose -> Head` depending on intended low-poly topology
  - `Head -> Body`
  - `Tail -> Body`
  - `Forelimb_* -> Body`
  - `Hindlimb_* -> Body`
  - segmented limb relations such as lower-limb to upper-limb when the
    creature build keeps those masses separate
- expanding truth-bundle pairing and ranking behavior beyond a narrow
  primary-anchor view so the loop can carry multiple failing creature seams at
  once
- tightening success criteria so "one local pair improved" or "overlap removed"
  is not enough when the assembled creature still has detached masses
- aligning `truth_followup`, `correction_candidates`, macro selection, and
  macro outcome semantics with those assembled-creature attachment requirements
- adding regression coverage around full-creature attachment integrity instead
  of only single-pair disjoint/overlap resolution
- requiring the meaningful E2E layer checks for those cases:
  - bbox relation
  - mesh-surface gap/contact semantics
  - overlap dimensions / overlap removal
  - contact assertion outcome
  - the final attachment verdict for the creature part relationship
- requiring Blender-backed assembled-creature E2E scenarios that prove multiple
  required seams are checked in the same run instead of only one pair at a time

This follow-on does **not** cover:

- prompt/client schema drift under [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md)
- anatomy-aware creature reconstruction under [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
- general hard-surface contact semantics already covered by earlier truth-layer
  work

## Acceptance Criteria

- the repo distinguishes "remove overlap" from "seat/attach this organic part"
  on the creature-guided path
- the assembled-creature truth path can surface and prioritize multiple failing
  required seams from one collection/object-set checkpoint instead of only
  whichever pair the current anchor logic happens to visit
- eyes, snout, nose, head/body, tail/body, and limb attachment relations no
  longer disappear from the loop while still visibly detached
- `truth_followup` / `correction_candidates` can communicate that attachment
  semantics are still wrong even when raw overlap is zero and even when another
  local pair already looks acceptable
- bounded next-step guidance favors the right repair family for organic seating
  cases instead of reusing generic overlap cleanup by default
- focused regressions protect the concrete squirrel-style failure shapes seen in
  the real assembled-creature run, not only isolated single-pair toy cases
- E2E coverage proves the correct truth layers are being exercised, not just
  visual or prose outcomes:
  - `scene_measure_gap` / contact semantics distinguish bbox-touching from real
    mesh-surface separation
  - `scene_measure_overlap` / overlap dimensions confirm whether geometry is
    still intersecting
  - `scene_assert_contact` or equivalent truth assertions participate in the
    success/failure verdict
  - collection/object-set stage checks report the expected failing creature seam
    set for the assembled target
  - the Blender-backed assembled-creature E2E matrix includes at least:
    - one face/head seam
    - one torso/body seam
    - one limb seam
  - the final result can differentiate:
    - seated/attached correctly
    - floating with a gap
    - intersecting / growing out of the surface

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/application/tool_handlers/macro_handler.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
- `tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py`
- `tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
- `tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py`
- `tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- focused E2E coverage that asserts bbox, mesh-surface gap/contact, overlap,
  attachment verdicts, and multi-pair seam coverage for assembled creature
  targets

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-142-01](./TASK-142-01_Creature_Part_Attachment_Taxonomy_And_Truth_Surface.md) | Define the required assembled-creature seam set and carry it into multi-pair truth/followup/candidate planning instead of relying on a narrow anchor-only view |
| 2 | [TASK-142-02](./TASK-142-02_Bounded_Macro_Selection_And_Repair_Behavior_For_Organic_Seating.md) | Align macro selection and bounded repair behavior with those assembled attachment semantics so local pair fixes stop masking a still-detached creature |
| 3 | [TASK-142-03](./TASK-142-03_Regression_And_Documentation_Pack_For_Organic_Attachment_Semantics.md) | Lock the new assembled-creature attachment semantics with focused unit/E2E truth-layer coverage and the corresponding operator-facing docs |

## Status / Board Update

- promote this as a board-level follow-on from the first real `TASK-128`
  squirrel run
- keep it separate from `TASK-141` because this is geometric/semantic repair
  behavior, not prompt/schema drift
- keep board tracking on this parent unless one execution slice needs to be
  promoted independently
- treat `TASK-142-01` through `TASK-142-03` as the canonical technical
  execution tree for this follow-on

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/tools/macro/test_macro_align_part_with_contact.py tests/unit/tools/macro/test_macro_cleanup_part_intersections.py tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run mypy server/adapters/mcp/areas/reference.py server/adapters/mcp/contracts/scene.py`
- `poetry run pytest tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/vision/test_reference_stage_truth_handoff.py`
