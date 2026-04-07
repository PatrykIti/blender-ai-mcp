# TASK-142-03-02: E2E Truth-Layer Coverage and Prompt/Docs for Creature Attachment

**Parent:** [TASK-142-03](./TASK-142-03_Regression_And_Documentation_Pack_For_Organic_Attachment_Semantics.md)
**Depends On:** [TASK-142-03-01](./TASK-142-03-01_Unit_Regression_Pack_For_Creature_Part_Seating_Truth.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Blender-backed assembled
creature E2E coverage now proves multi-pair seam reporting for face/head,
torso/body, and limb/body relations, and the prompt/docs layer now uses the
same required-seam and attachment-verdict vocabulary as the runtime.

## Objective

Prove the targeted creature-part attachment semantics end to end and align the
operator-facing docs to the same truth-layer verdict model for a full
assembled-creature run.

## Business Problem

The specific `TASK-142` failure shapes are easy to misjudge visually, and the
current E2E pack is still too single-pair-heavy for the actual squirrel failure
mode:

- bbox touching can still hide a mesh-surface gap
- overlap removal can still leave the part floating
- a creature part can still look like it grows out of the surface incorrectly
- a full assembled creature can still have many detached seams even when one
  or two focused pair checks already pass

This leaf owns the Blender-backed E2E proof and the matching docs language so
the runtime and operator story do not drift apart.

## Repository Touchpoints

- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- E2E coverage proves the targeted truth layers participate in the final
  verdict for creature-part attachment cases
- E2E coverage includes at least one Blender-backed assembled-creature scenario
  where several required seams are detached at once
- the assembled-creature E2E matrix includes at least:
  - one face/head seam such as `Eye_* -> Head` or `Snout/Nose -> Head`
  - one torso/body seam such as `Head -> Body` or `Tail -> Body`
  - one limb seam such as `Forelimb/Hindlimb -> Body` or distal-to-proximal
    limb seating
- prompt/docs wording matches the shipped attachment taxonomy and verdict model
- the repo documents the difference between:
  - seated/attached correctly
  - floating with a measurable gap
  - intersecting / growing through the surface

## Leaf Work Items

- add or update E2E truth-layer scenarios for the targeted creature-part pairs
- add one assembled-creature E2E pack that exercises multiple failing seams in
  one run, not only isolated single-pair checks
- make that assembled-creature pack prove at least one face/head seam, one
  torso/body seam, and one limb seam in the same coverage wave
- align prompt/docs wording to the same attachment verdict semantics
- ensure board/task summaries stay consistent with the shipped E2E/docs scope

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- update the parent summary so it explicitly names the shipped assembled-creature
  E2E truth-layer coverage and docs scope when this leaf closes
