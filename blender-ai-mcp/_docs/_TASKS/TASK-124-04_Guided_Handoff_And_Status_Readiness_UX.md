# TASK-124-04: Guided Handoff and Status Readiness UX

**Parent:** [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** Guided router surfaces now expose reference-session
readiness directly on `router_set_goal(...)` and `router_get_status()`, so the
next required action is available from typed payloads instead of hidden state.

## Objective

Expose the next required action for guided reference sessions through
`router_get_status()` and guided handoff/status payloads, not just through
operator folklore.

## Business Problem

Even with better internal session semantics, the product still fails if the
model cannot tell:

- whether the goal is active
- whether the references are active vs pending
- whether compare/iterate is safe to call now
- what it should do next if not

This should come from the surface/runtime, not from a lucky prompt.

## Technical Direction

Extend status/handoff UX so the current guided state can say things like:

- goal active, attach references now
- pending references exist, activate goal before compare
- session ready for stage compare / iterate

This can be a dedicated readiness payload or a small extension of existing
guided/status contracts, but it must remain explicit and typed.

## Repository Touchpoints

- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/router/application/test_router_contracts.py`

## Acceptance Criteria

- router status/handoff payloads expose guided reference readiness explicitly
- the next required action is available without reading long prose blobs
- the UX works for `guided_manual_build` paths, not only workflow-ready paths

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/router/application/test_router_contracts.py`

## Changelog Impact

- include in the parent task changelog entry when shipped
