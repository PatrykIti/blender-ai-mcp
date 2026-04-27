# TASK-142-03: Regression and Documentation Pack for Organic Attachment Semantics

**Parent:** [TASK-142](./TASK-142_Creature_Part_Seating_And_Organic_Attachment_Semantics.md)
**Depends On:** [TASK-142-01](./TASK-142-01_Creature_Part_Attachment_Taxonomy_And_Truth_Surface.md), [TASK-142-02](./TASK-142-02_Bounded_Macro_Selection_And_Repair_Behavior_For_Organic_Seating.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Added focused unit coverage
for required seam planning and attachment semantics, added a Blender-backed
assembled-creature truth-layer pack for multi-pair seam coverage, and aligned
the operator-facing docs to the shipped attachment verdict model.

## Objective

Lock the new organic attachment semantics with focused unit/E2E truth-layer
coverage and synchronize the operator-facing docs to the same verdict model for
full assembled-creature runs, not just isolated pair examples.

## Business Problem

`TASK-142` only matters if the repo can prove the new semantics on the exact
creature-part failure shapes that motivated it. The current repo already has
some useful single-pair E2E coverage, but that still falls short of the real
problem:

- contract-level truth/candidate regressions
- macro-level bounded repair regressions
- E2E truth assertions that distinguish bbox touching from real surface
  attachment
- assembled-creature E2E coverage that proves multiple required seams are
  surfaced together
- docs that tell the operator what those verdicts mean

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
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

- unit coverage protects the targeted creature-part attachment semantics and
  macro selection/reporting behavior
- E2E coverage proves the correct truth layers participate in the verdict:
  - bbox relation
  - mesh-surface gap/contact semantics
  - overlap dimensions / overlap removal
  - contact assertion outcome
  - final attachment verdict
- regression scope explicitly includes not only face/head attachments but also
  head/body, tail/body, and limb attachment seams on the creature path
- regression scope includes at least one Blender-backed assembled-creature
  scenario where multiple required seams fail together and the truth/candidate
  path reports them together
- the assembled-creature E2E matrix includes at least:
  - one face/head seam
  - one torso/body seam
  - one limb seam
- prompt/docs guidance uses the same attachment vocabulary and verdict model as
  the runtime/tests path

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`

## Changelog Impact

- include in the parent `TASK-142` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-142-03-01](./TASK-142-03-01_Unit_Regression_Pack_For_Creature_Part_Seating_Truth.md) | Add focused unit coverage for required seam planning, truth-followup, macro selection, and attachment verdict semantics |
| 2 | [TASK-142-03-02](./TASK-142-03-02_E2E_Truth_Layer_Coverage_And_Prompt_Docs_For_Creature_Attachment.md) | Add Blender-backed assembled-creature truth-layer coverage plus the matching operator-facing docs story |

## Status / Board Update

- keep board tracking on the parent `TASK-142`
- do not promote this subtask independently unless regression/docs work
  becomes the final remaining slice
