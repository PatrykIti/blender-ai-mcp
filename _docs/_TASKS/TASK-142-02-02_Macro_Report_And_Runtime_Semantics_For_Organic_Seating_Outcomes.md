# TASK-142-02-02: Macro Report and Runtime Semantics for Organic Seating Outcomes

**Parent:** [TASK-142-02](./TASK-142-02_Bounded_Macro_Selection_And_Repair_Behavior_For_Organic_Seating.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make bounded macro reports and runtime follow-up semantics reflect whether a
targeted creature part is actually seated/attached correctly, not just whether
raw overlap dropped to zero, and not just whether one local seam improved while
the assembled creature remains detached elsewhere.

## Business Problem

Macro execution today can still produce the wrong success story for targeted
organic parts:

- overlap is gone
- the part is still floating or visibly wrong
- or one pair is fixed while the broader assembled creature still has detached
  seams
- the report still looks close to done

This leaf owns the runtime/reporting semantics that decide whether a bounded
repair really resolved the intended creature-part relation and how much of the
remaining creature still needs follow-up.

## Repository Touchpoints

- `server/application/tool_handlers/macro_handler.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py`
- `tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py`
- `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- bounded macro reports can distinguish:
  - seated/attached correctly
  - floating with a gap
  - intersecting / growing through the surface
- verification guidance on the targeted organic pairs aligns with the intended
  attachment verdict, not only overlap removal
- cleanup-oriented macro reports stop implying semantic success when the
  targeted pair still fails the intended attachment outcome
- collection/run-level follow-up semantics can still highlight unresolved
  attachment seams after a local macro success

## Leaf Work Items

- align macro reports and verification guidance with the targeted attachment
  outcomes
- add focused unit coverage for the repaired vs still-wrong verdicts
- add or update Blender-backed seams where the targeted truth assertions are
  exercised after macro repair, including more than one creature seam family

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py`
- `tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py`
- `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
- `tests/e2e/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-142`
- update the parent summary so it explicitly calls out the shipped macro/report
  outcome semantics and their assembled-creature follow-up behavior when this
  leaf closes
