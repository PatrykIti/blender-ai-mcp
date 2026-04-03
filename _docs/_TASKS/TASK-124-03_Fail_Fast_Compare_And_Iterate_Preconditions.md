# TASK-124-03: Fail-Fast Compare and Iterate Preconditions

**Parent:** [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Make `reference_compare_stage_checkpoint(...)` and
`reference_iterate_stage_checkpoint(...)` fail fast with one clear next action
when guided reference-session preconditions are not met.

## Business Problem

Compare/iterate calls should not proceed in a half-valid state.

Today they can still be invoked when:

- no active goal exists
- only pending references exist
- reference attachments do not match the active goal/session

When that happens, the model can waste context budget trying to repair session
state manually instead of receiving one deterministic next step.

## Technical Direction

Add explicit precondition guards and error semantics such as:

- `active_goal_required`
- `pending_references_detected`
- `reference_session_not_ready`

The response should make the next required action obvious and should prefer
structured fields over only prose.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/`

## Acceptance Criteria

- compare/iterate paths fail fast when the session is not ready
- the returned reason and next action are deterministic and machine-readable
- the model no longer needs to improvise recovery steps after a null-goal run

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/` when runtime behavior changes

## Changelog Impact

- include in the parent task changelog entry when shipped
