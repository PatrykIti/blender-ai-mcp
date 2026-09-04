# TASK-150-03-03-04: Router Execution Guards And Blocked Response Policy

**Parent:** [TASK-150-03-03](./TASK-150-03-03_Generic_Families_Part_Roles_And_Execution_Enforcement.md)
**Depends On:** [TASK-150-03-03-01](./TASK-150-03-03-01_Shared_Tool_Family_Vocabulary_And_Overlay_Mapping.md), [TASK-150-03-03-02](./TASK-150-03-03-02_Guided_Part_Role_Registry_And_Session_Contracts.md), [TASK-150-03-03-03](./TASK-150-03-03-03_Guided_Register_Part_And_Role_Hint_Input_Path.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Move TASK-150 from visibility-only gating to real execution-time enforcement by
adding family/role guards in the router/firewall path.

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/router/application/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/router/`

## Acceptance Criteria

- router/firewall can determine the family of the final tool call
- execution can be blocked when:
  - the family is not allowed for the current step
  - the role is not allowed for the current step
  - required role groups are still incomplete
- blocked responses return structured guidance including:
  - current step
  - blocked family or role
  - allowed families/roles
  - next actions or missing role groups

## Detailed Implementation Notes

- put the enforcement in one shared execution path rather than in dozens of
  MCP wrappers
- likely integration point:
  - `route_tool_call_report(...)`
- keep existing correction/override behavior, then evaluate guided execution
  policy against the final effective tool call
- fail closed on guided surfaces for real family/role violations
- keep `legacy-flat` and explicitly broad/manual surfaces outside this policy

## Current Code Anchors

- `server/adapters/mcp/router_helper.py`
  - lines 247-404: current `route_tool_call_report(...)`
  - lines 315-376: current corrected/direct execution path
- `server/adapters/mcp/session_capabilities.py`
  - lines 252-314: current initial flow-state creation
  - lines 1107-1149: current iterate-based step advancement

## Pseudocode Sketch

```python
policy = evaluate_guided_execution_policy(
    tool_name=tool_to_execute,
    params=tool_params,
    flow_state=session.guided_flow_state,
    part_registry=session.guided_part_registry,
)
if policy.status == "blocked":
    return MCPExecutionReport(
        router_disposition="failed_closed_error",
        error=policy.message,
        guided_flow_state=policy.updated_flow_state,
    )
```

## Planned Unit Test Scenarios

- wrong family is blocked before the direct executor runs
- wrong role is blocked even when the tool itself is visible and otherwise
  valid
- missing required role groups block the call with typed guidance
- `legacy-flat` stays outside the guided fail-closed policy

## Planned E2E / Transport Scenarios

- stdio guided creature session:
  - `ear_pair` creation blocked during `create_primary_masses`
- streamable guided creature session:
  - `macro_finish_form` blocked until `checkpoint_iterate` / `finish`
- no-match/manual path:
  - direct build tool call still gets blocked by router/firewall policy

## Execution Structure

| Order | Micro-Leaf | Purpose |
|------|------------|---------|
| 1 | [TASK-150-03-03-04-01](./TASK-150-03-03-04-01_Family_Resolution_And_Role_Lookup_In_Route_Tool_Call.md) | Resolve tool family and role context inside the shared router execution path |
| 2 | [TASK-150-03-03-04-02](./TASK-150-03-03-04-02_Blocked_Response_Envelope_And_Fail_Closed_Policy.md) | Return structured blocked responses and fail closed on guided surfaces when family/role policy is violated |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`
- `tests/e2e/integration/test_guided_flow_step_gating.py`

## Changelog Impact

- include in the parent TASK-150 execution-enforcement changelog entry

## Completion Summary

- route-time family/role lookup now exists in the shared execution path
- guided surfaces can fail closed on wrong family or explicit role before the
  tool executor runs
- this still leaves later follow-on work for deeper role-group completion
  transitions and broader regression/E2E coverage
