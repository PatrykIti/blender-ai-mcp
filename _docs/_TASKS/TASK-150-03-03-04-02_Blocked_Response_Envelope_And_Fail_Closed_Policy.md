# TASK-150-03-03-04-02: Blocked Response Envelope And Fail-Closed Policy

**Parent:** [TASK-150-03-03-04](./TASK-150-03-03-04_Router_Execution_Guards_And_Blocked_Response_Policy.md)
**Depends On:** [TASK-150-03-03-04-01](./TASK-150-03-03-04-01_Family_Resolution_And_Role_Lookup_In_Route_Tool_Call.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Return structured blocked responses and fail closed on guided surfaces when one
tool call violates family/role execution policy.

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/contracts/router.py`

## Current Code Anchors

- `router_helper.py` lines 378-404: current fail-closed / fail-open branch

## Planned Code Shape

```python
if policy.blocked:
    return MCPExecutionReport(
        router_disposition="failed_closed_error",
        error=policy.message,
        guided_flow_state=policy.guided_flow_state,
    )
```

## Acceptance Criteria

- guided surfaces fail closed on family/role violations
- the response explains current step, allowed families/roles, and next actions

## Completion Summary

- added fail-closed guided execution checks for:
  - disallowed shared families
  - disallowed explicit guided roles
- integrated those checks into the shared `route_tool_call_report(...)` path
- documented the new blocked-response semantics in MCP/prompt docs

## Planned Unit Test Scenarios

- blocked report contains current step and guidance fields
- fail-closed path does not fall through to direct execution on `llm-guided`
- manual/broad surfaces still follow the existing non-guided behavior

## Planned E2E / Transport Scenarios

- blocked call over stdio returns a stable typed error instead of a silent
  disappearance from `search_tools(...)` only

## Tests To Add/Update

- `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`
