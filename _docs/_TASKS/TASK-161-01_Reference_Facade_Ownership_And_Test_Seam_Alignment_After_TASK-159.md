# TASK-161-01: Reference Facade Ownership And Test Seam Alignment After TASK-159

**Parent:** [TASK-161](./TASK-161_TASK-159_Closeout_Seam_And_Proof_Lane_Alignment.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Finish the remaining `reference.py` closeout so the facade keeps staged compare
assembly, while the extracted truth/planner modules own the helper logic and
the reference unit lane validates those modules directly.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_truth.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- keep public `reference_*` tool behavior stable
- keep adapter-owned injection wrappers such as `_assembled_target_scope(...)`
  and `_build_correction_truth_bundle(...)` where they still need repo wiring
- move/bind the remaining truth-budget and correction-candidate helper ownership
  to the helper modules, then update tests to import those helpers there

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`

## Docs To Update

- inherit parent docs closeout unless helper ownership wording needs adjustment

## Changelog Impact

- include in the parent `TASK-161` changelog entry when shipped

## Acceptance Criteria

- `reference.py` no longer keeps the residual truth/planner helper ownership by
  default
- the main reference unit lane no longer imports those helpers from the facade
  when the extracted module is the real owner

## Status / Board Update

- completed as a historical child of `TASK-161`
- no separate promoted board row is needed for this slice

## Completion Summary

Completed on 2026-05-05.

- rewired the remaining truth/planner helper ownership through the extracted
  helper modules
- aligned the reference unit lane so the extracted modules, not the facade, are
  the direct proof seam for the moved helpers
