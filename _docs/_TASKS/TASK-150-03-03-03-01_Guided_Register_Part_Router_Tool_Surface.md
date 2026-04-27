# TASK-150-03-03-03-01: Guided Register Part Router Tool Surface

**Parent:** [TASK-150-03-03-03](./TASK-150-03-03-03_Guided_Register_Part_And_Role_Hint_Input_Path.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Add one minimal guided-only tool for registering object roles in the current
guided session.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/session_capabilities.py`

## Current Code Anchors

- `areas/router.py` top-of-file router public tool registration list
- `areas/router.py` lines 330-396: existing goal/status bootstrap style

## Planned Code Shape

```python
async def guided_register_part(
    ctx: Context,
    object_name: str,
    role: str,
    role_group: str | None = None,
) -> RouterStatusContract:
    ...
```

## Acceptance Criteria

- one canonical role-registration surface exists
- tool returns updated guided-flow state or status payload

## Completion Summary

- added `guided_register_part(...)` on the router MCP surface
- wired it to update the internal guided part registry for the active guided
  session
- returned refreshed guided status so callers can immediately see updated role
  summaries
- documented the tool as the canonical semantic part-registration path on the
  guided surface

## Planned Unit Test Scenarios

- `guided_register_part(...)` stores role + role_group in session state
- repeated registration for the same object updates instead of duplicating
- invalid role names return a typed error

## Planned E2E / Transport Scenarios

- guided creature stdio session:
  - create `Squirrel_Body`
  - register it as `body_core`
  - `router_get_status()` shows `completed_roles=["body_core"]`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
