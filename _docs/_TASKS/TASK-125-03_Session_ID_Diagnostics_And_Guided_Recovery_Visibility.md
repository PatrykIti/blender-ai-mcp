# TASK-125-03: Session ID Diagnostics and Guided Recovery Visibility

**Parent:** [TASK-125](./TASK-125_MCP_Transport_Mode_Switching_And_Session_Diagnostics.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Guided/router/reference payloads now expose explicit
`session_id` and `transport` diagnostics, making MCP session resets visible in
normal product responses instead of only in server logs.

## Objective

Expose explicit MCP session identifiers and recovery-facing session diagnostics
on the guided/router/reference surfaces.

## Business Problem

Current guided/session-aware flows can lose visible session state without
showing enough information to explain whether:

- the MCP session changed
- the server process changed
- or only the Blender scene changed

That forces operators to infer transport/runtime failures from indirect clues.

## Technical Direction

Add explicit MCP session diagnostics, at minimum:

- current session ID on `router_get_status()`
- transport-aware/session-aware recovery hints on guided/reference fail-fast
  paths where state is missing

Prefer typed/session fields over long prose-only diagnostics.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/session_state.py`
- `tests/unit/adapters/mcp/`

## Acceptance Criteria

- `router_get_status()` exposes an explicit MCP session identifier
- guided/reference recovery diagnostics can distinguish likely MCP session loss
  from Blender-scene loss
- the same diagnostics work in both supported transport modes

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md` if operator guidance changes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- contract/docs parity coverage as needed

## Changelog Impact

- include in the parent task changelog entry when shipped
