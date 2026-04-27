# TASK-150-03-03-06-01: Unit And Transport Regression Matrix For Family/Role Enforcement

**Parent:** [TASK-150-03-03-06](./TASK-150-03-03-06_Regression_And_Docs_For_Execution_Enforcement.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Build the regression matrix that proves family/role execution enforcement
works across unit and transport-backed guided sessions.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_flow_step_gating.py`
- `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`

## Planned Matrix

- unit:
  - blocked secondary-part creation during `create_primary_masses`
  - allowed body/head creation during `create_primary_masses`
  - blocked finish-family action before `checkpoint_iterate`
- transport:
  - no-match/manual creature path
  - stdio same-session role registration + unlock
  - streamable same-session role registration + unlock

## Acceptance Criteria

- the server proves real execution blocking, not just visibility shaping

## Completion Summary

- added transport-backed guided-surface regressions for:
  - blocked build calls without explicit or registered roles
  - canonical `guided_register_part(...)` role registration
  - same-session unlock from primary roles into secondary-part execution
  - immediate secondary-part success after the step transition
- updated stdio parity expectations to include the new router surface tool
  `guided_register_part`

## Pseudocode Sketch

```python
blocked = call_tool("modeling_create_primitive", {"guided_role": "ear_pair", ...})
assert blocked["guided_flow_state"]["current_step"] == "create_primary_masses"
assert "allowed_roles" in blocked["error"]
```

## Planned Unit Test Scenarios

- blocked `ear_pair` during `create_primary_masses`
- allowed `body_core` during `create_primary_masses`
- blocked `finish` action before checkpoint/iterate
- unlocked `secondary_parts` after required primary role groups complete

## Planned E2E / Transport Scenarios

- stdio:
  - create/register primary roles
  - verify `search_tools(...)` now exposes secondary-part tools
- streamable:
  - same session survives role registration and unlock without requiring a
    manual router status refresh
- manual-handoff creature path:
  - transport-backed block message includes current step and missing roles
