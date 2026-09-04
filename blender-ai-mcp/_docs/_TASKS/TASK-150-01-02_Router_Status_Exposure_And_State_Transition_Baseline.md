# TASK-150-01-02: Router/Status Exposure And State-Transition Baseline

**Parent:** [TASK-150-01](./TASK-150-01_Guided_Flow_State_Contract_And_Session_Model.md)
**Depends On:** [TASK-150-01-01](./TASK-150-01-01_Flow_State_Types_Contracts_And_Session_Keys.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Expose the new flow state through `router_set_goal(...)` / `router_get_status()`
and define the baseline transition semantics from goal-setting into the first
server-driven flow step.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Planned File Work

- Modify:
  - `server/adapters/mcp/areas/router.py`
  - `server/adapters/mcp/session_capabilities.py`
  - `tests/unit/adapters/mcp/test_router_elicitation.py`
  - `tests/e2e/router/test_guided_manual_handoff.py`

## Detailed Implementation Notes

- initialize `guided_flow_state` at the same point where `guided_handoff` is
  attached, so both contracts describe the same transition rather than racing
  each other
- keep the first baseline transition deterministic:
  - `router_set_goal(...)` -> `guided_flow_state.current_step`
  - no free-form model interpretation required
- expose `guided_flow_state` on:
  - `RouterGoalResponseContract`
  - `RouterStatusContract`
- do not yet make flow-state mutation happen inside arbitrary tool handlers;
  this leaf should only establish the baseline state on goal-setting and
  status retrieval

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_router_elicitation.py`
  - goal with no-match creature handoff initializes creature-profile flow state
  - generic/no-specialized goal initializes generic profile flow state
  - `router_get_status()` mirrors the same `guided_flow_state`
- Modify `tests/e2e/router/test_guided_manual_handoff.py`
  - end-to-end area test that `router_set_goal(...)` returns both
    `guided_handoff` and `guided_flow_state`
  - status call in the same session returns the same `flow_id`,
    `domain_profile`, and `current_step`

## Example Test Sketch

```python
def test_router_set_goal_creature_goal_initializes_flow_state(...):
    result = asyncio.run(router_set_goal(ctx, goal="create a low-poly squirrel ..."))
    assert result.guided_flow_state is not None
    assert result.guided_flow_state.domain_profile == "creature"
    assert result.guided_flow_state.current_step == "establish_spatial_context"
```

## Acceptance Criteria

- `router_set_goal(...)` can initialize `guided_flow_state`
- `router_get_status(...)` returns the active flow state
- the first transition after goal-setting is deterministic and typed
- no-match/manual handoff still works, but now carries concrete flow-step state

## Pseudocode Sketch

```python
result = handler.set_goal(goal, resolved_params)
guided_handoff = build_guided_handoff_payload(...)
guided_flow_state = initialize_guided_flow_state(
    goal=goal,
    guided_handoff=guided_handoff,
    router_result=result,
)
state = update_session_from_router_goal_async(..., guided_flow_state=guided_flow_state)
result["guided_flow_state"] = guided_flow_state
```

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped

## Completion Summary

- `router_set_goal(...)` and `router_get_status()` now expose `guided_flow_state`
- same-session goal/status paths return the active flow state deterministically
- no-match/manual handoff now carries typed flow-step state
