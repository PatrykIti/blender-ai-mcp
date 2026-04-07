# TASK-142-03-01: Unit Regression Pack for Creature-Part Seating Truth

**Parent:** [TASK-142-03](./TASK-142-03_Regression_And_Documentation_Pack_For_Organic_Attachment_Semantics.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Unit regressions now protect
required seam expansion, attachment-semantics truth handoff, macro selection,
and macro/MCP attachment-verdict reporting for guided creature scope.

## Objective

Add focused unit coverage for the targeted attachment taxonomy, truth-surface
evidence, required seam planning, macro selection, and bounded repair verdict
semantics.

## Business Problem

The targeted creature-part semantics sit across several layers:

- pair classification
- required seam expansion from collection/object-set scope
- truth-followup items
- correction-candidate evidence
- macro-family selection
- macro-report outcome semantics

If those layers are not covered together, the repo can regress into generic
gap/overlap logic or anchor-only pair logic without any immediate signal.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py`
- `tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py`
- `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`

## Acceptance Criteria

- unit tests protect the targeted taxonomy and truth-surface semantics
- unit tests protect the required seam planner / pair-expansion behavior for
  assembled creature scope
- unit tests protect the chosen macro-family selection policy
- unit tests protect the repaired vs still-wrong attachment verdict semantics

## Leaf Work Items

- add truth-followup/correction-candidate regressions for the targeted
  creature-part relations
- add pair-planning regressions for collection/object-set assembled creature
  scope
- add macro-selection regressions for overlap vs attachment cases
- add macro-report regressions for seated vs floating vs intersecting outcomes

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py`
- `tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py`
- `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- update the parent summary so it explicitly names the shipped unit-regression
  seams and required pair-planning coverage when this leaf closes
