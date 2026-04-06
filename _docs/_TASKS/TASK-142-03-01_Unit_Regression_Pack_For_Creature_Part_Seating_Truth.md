# TASK-142-03-01: Unit Regression Pack for Creature-Part Seating Truth

**Parent:** [TASK-142-03](./TASK-142-03_Regression_And_Documentation_Pack_For_Organic_Attachment_Semantics.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add focused unit coverage for the targeted attachment taxonomy, truth-surface
evidence, macro selection, and bounded repair verdict semantics.

## Business Problem

The targeted creature-part semantics sit across several layers:

- pair classification
- truth-followup items
- correction-candidate evidence
- macro-family selection
- macro-report outcome semantics

If those layers are not covered together, the repo can regress into generic
gap/overlap logic without any immediate signal.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`

## Acceptance Criteria

- unit tests protect the targeted taxonomy and truth-surface semantics
- unit tests protect the chosen macro-family selection policy
- unit tests protect the repaired vs still-wrong attachment verdict semantics

## Leaf Work Items

- add truth-followup/correction-candidate regressions for the targeted
  creature-part relations
- add macro-selection regressions for overlap vs attachment cases
- add macro-report regressions for seated vs floating vs intersecting outcomes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- update the parent summary so it explicitly names the shipped unit-regression
  seams when this leaf closes
