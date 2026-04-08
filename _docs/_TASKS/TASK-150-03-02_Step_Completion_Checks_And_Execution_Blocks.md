# TASK-150-03-02: Step Completion Checks And Execution Blocks

**Parent:** [TASK-150-03](./TASK-150-03_Step_Gated_Visibility_And_Execution_Policy.md)
**Depends On:** [TASK-150-03-01](./TASK-150-03-01_Flow_Aware_Visibility_Rules_And_Search_Surface_Gating.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define how required checks and blocked families stop the model from moving to
later-stage actions prematurely.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/integration/`

## Planned File Work

- Modify:
  - `server/adapters/mcp/areas/router.py`
  - `server/adapters/mcp/session_capabilities.py`
  - `server/adapters/mcp/discovery/search_surface.py`
  - `tests/unit/adapters/mcp/test_router_elicitation.py`
  - `tests/e2e/integration/test_guided_flow_step_gating.py`
  - `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`

## Acceptance Criteria

- later-stage tool families can be blocked until required checks are complete
- the block path returns structured guidance instead of silent failure
- the flow can require checkpoint/iterate or inspect/validate before allowing
  certain next actions

## Pseudocode Sketch

```python
def can_use_tool(tool_name, flow_state):
    if tool_name in flow_state.blocked_families:
        return blocked("family blocked until required checks complete")
    if flow_state.required_checks and not flow_state.completed_required_checks:
        return blocked("run required checks first", next_actions=flow_state.required_checks)
    return allow()
```

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_router_elicitation.py`
  - blocked family returns structured guidance with `next_actions`
  - completing required checks clears the block
- Create `tests/e2e/integration/test_guided_flow_step_gating.py`
  - stdio same-session:
    - `router_set_goal(...)`
    - assert initial flow step
    - try a blocked later-stage tool family
    - assert structured block
    - perform required step/check
    - assert the family becomes available/searchable
- Create `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`
  - no-match/manual path
  - workflow-ready path
  - both must produce coherent step-gated behavior

## Example E2E Sketch

```python
async def test_guided_flow_blocks_finish_family_before_checkpoint(...):
    goal = await client.call_tool("router_set_goal", {...})
    status = await client.call_tool("router_get_status", {})
    assert status["guided_flow_state"]["current_step"] == "create_primary_masses"

    blocked = await client.call_tool("call_tool", {"name": "macro_finish_form", "arguments": {...}})
    assert "required_checks" in blocked["error"] or blocked["guided_flow_state"]["step_status"] == "blocked"

    await client.call_tool("scene_scope_graph", {...})
    await client.call_tool("reference_iterate_stage_checkpoint", {...})

    status = await client.call_tool("router_get_status", {})
    assert status["guided_flow_state"]["current_step"] != "create_primary_masses"
```

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/integration/test_guided_flow_step_gating.py`
- `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped
