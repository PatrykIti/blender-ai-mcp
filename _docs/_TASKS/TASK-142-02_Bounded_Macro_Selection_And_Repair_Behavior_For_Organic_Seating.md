# TASK-142-02: Bounded Macro Selection and Repair Behavior for Organic Seating

**Parent:** [TASK-142](./TASK-142_Creature_Part_Seating_And_Organic_Attachment_Semantics.md)
**Depends On:** [TASK-142-01](./TASK-142-01_Creature_Part_Attachment_Taxonomy_And_Truth_Surface.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Align bounded macro selection and repair behavior with the creature-part
attachment taxonomy so the guided loop stops defaulting to the wrong repair
family across head, face, torso, tail, and limb attachment relations, even
when the assembled creature has several failing seams at once.

## Business Problem

Even with a good truth surface, the session will still regress if the bounded
repair path keeps choosing the wrong macro or treats one repaired pair as a
proxy for the whole creature:

- `macro_cleanup_part_intersections` is good for removing raw overlap
- `macro_align_part_with_contact` is better for small seating/contact repair
- `macro_attach_part_to_surface` is the better family when the task is to seat
  a part onto or into another organic mass
- one local macro success is not enough if several other required seams are
  still detached

This subtask owns the deterministic policy for picking among those families and
for reporting what a bounded repair actually achieved in a multi-seam creature
run.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/application/tool_handlers/macro_handler.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- overlap cleanup is no longer the default answer for attachment/seating cases
  that should stay in seated contact
- bounded macro selection can distinguish when to prefer:
  - `macro_cleanup_part_intersections`
  - `macro_align_part_with_contact`
  - `macro_attach_part_to_surface`
- macro/runtime reports do not imply success for targeted organic pairs just
  because raw overlap is gone
- macro/runtime reports do not let one repaired local seam hide the fact that
  several other required creature seams still need correction
- the chosen macro family remains bounded and deterministic; this task does not
  reopen free-form collision solving

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`

## Changelog Impact

- include in the parent `TASK-142` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-142-02-01](./TASK-142-02-01_Overlap_Cleanup_Vs_Attachment_Macro_Selection_Policy.md) | Define deterministic macro-family selection for overlap vs attachment cases across a multi-seam assembled creature |
| 2 | [TASK-142-02-02](./TASK-142-02-02_Macro_Report_And_Runtime_Semantics_For_Organic_Seating_Outcomes.md) | Align bounded macro reports and runtime verdicts with the targeted organic seating outcomes so local success does not hide a detached creature |

## Status / Board Update

- keep board tracking on the parent `TASK-142`
- do not promote this subtask independently unless macro-family behavior
  becomes the only remaining open slice
