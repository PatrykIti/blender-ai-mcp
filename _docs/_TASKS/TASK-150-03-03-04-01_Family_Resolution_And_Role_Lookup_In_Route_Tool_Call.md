# TASK-150-03-03-04-01: Family Resolution And Role Lookup In Route Tool Call

**Parent:** [TASK-150-03-03-04](./TASK-150-03-03-04_Router_Execution_Guards_And_Blocked_Response_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Resolve tool family and role context in the shared router execution path before
the final tool call is executed.

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`

## Current Code Anchors

- lines 247-404: `route_tool_call_report(...)`
- lines 336-355: corrected-tool execution loop

## Planned Code Shape

```python
family = resolve_guided_tool_family(tool_to_execute)
role_context = resolve_guided_role_context(tool_to_execute, tool_params, session_state)
policy = evaluate_guided_execution_policy(family, role_context, flow_state)
```

## Acceptance Criteria

- the router path can resolve family + role before executing the final tool
- both direct and corrected calls use the same policy evaluation point

## Planned Unit Test Scenarios

- direct `modeling_create_primitive` resolves to `primary_masses`
- corrected tool sequences still resolve family/role from the final effective
  tool call
- family resolution works for both atomic tools and macros

## Planned E2E / Transport Scenarios

- not required at this micro-leaf; proven indirectly by execution-block E2E
  scenarios

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
