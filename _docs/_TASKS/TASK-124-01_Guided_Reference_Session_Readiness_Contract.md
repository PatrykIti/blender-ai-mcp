# TASK-124-01: Guided Reference Session Readiness Contract

**Parent:** [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Define one explicit readiness model for guided reference sessions instead of
relying on implicit ordering rules.

## Business Problem

The system currently has hidden session states such as:

- active goal present / absent
- reference images attached to active goal
- pending reference images waiting for adoption
- guided manual build handoff present or absent

But the compare/iterate tools and prompts do not expose this as one explicit
product contract.

That makes it easy for the model to land in "half-valid" states where:

- references exist, but only as pending
- goal_override is present, but `current_goal` is still null
- the model keeps retrying instead of knowing whether the session is actually
  ready

## Technical Direction

Add one explicit readiness payload/model that can answer questions like:

- is there an active goal?
- are there attached reference images for that goal?
- are there pending references still waiting for adoption?
- is the session ready for:
  - `reference_compare_stage_checkpoint(...)`
  - `reference_iterate_stage_checkpoint(...)`

Prefer explicit booleans / enums / reason fields over prose-only messages.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/`

## Acceptance Criteria

- one explicit readiness contract exists for guided reference sessions
- readiness can be computed without guessing from prose fields
- later compare/iterate logic can consume that contract directly

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`

## Changelog Impact

- include in the parent task changelog entry when shipped
