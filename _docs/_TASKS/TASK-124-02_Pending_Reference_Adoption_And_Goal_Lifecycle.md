# TASK-124-02: Pending Reference Adoption and Goal Lifecycle

**Parent:** [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Make pending reference adoption and goal lifecycle semantics deterministic and
session-safe.

## Business Problem

Today the product still allows this confusing pattern:

1. attach references before the goal exists
2. references become pending
3. set a goal
4. compare/iterate still does not behave as if the session is fully ready

That is operationally fragile because the model may then:

- reattach references unnecessarily
- use `goal_override` as a session substitute
- keep working inside a session that still has `current_goal == null`

## Technical Direction

Define exactly when pending references should be adopted:

- after `router_set_goal(...)` with a valid active goal
- across `ready` and `guided_manual_build` continuation paths when appropriate
- only within the same session / state boundary

Also define what happens when:

- the goal changes
- the goal is cleared
- pending references exist for a different intended goal

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- pending references are adopted deterministically when the session becomes
  eligible
- `guided_manual_build` flows do not lose references just because the path is a
  manual continuation rather than a workflow match
- goal clearing and goal changes leave the reference state explicit and
  predictable

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- include in the parent task changelog entry when shipped
