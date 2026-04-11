# TASK-155-02-04: Checkpoint Target Scope Enforcement

**Parent:** [TASK-155-02](./TASK-155-02_Governor_Workset_Refresh_And_Bootstrap_Discipline.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Prevent checkpoint calls from bypassing a failing assembled workset by narrowing
to a single safe object, such as `reference_iterate_stage_checkpoint(target_object="Body")`
after `Body + Head + Snout` was the active stage.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/application/services/spatial_graph.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- during active assembled-creature stages, checkpoint target scope must be
  compatible with the active workset or return an explicit guided warning/block
- one-object checkpoint iterations do not advance flow when required active
  seams remain outside the requested scope
- explicit single-object checkpoints remain valid when the current guided state
  truly has a single-object target
- the response explains the expected `target_objects=[...]` or
  `collection_name=...` shape

## Tests To Add/Update

- Unit:
  - add target-scope enforcement cases to
    `tests/unit/adapters/mcp/test_reference_images.py`
  - add flow-state scope compatibility coverage in
    `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- E2E:
  - extend `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
    with an assembled-scope checkpoint bypass attempt
  - keep `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
    proving multi-pair seams stay live

## Changelog Impact

- include in the TASK-155 changelog entry

## Completion Summary

- stage checkpoint compare/iterate now blocks active assembled-workset bypasses
  that narrow to a single safe object while required seams remain out of scope
