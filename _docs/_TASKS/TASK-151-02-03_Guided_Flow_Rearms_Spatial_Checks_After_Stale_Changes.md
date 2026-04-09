# TASK-151-02-03: Guided Flow Rearms Spatial Checks After Stale Changes

**Parent:** [TASK-151-02](./TASK-151-02_Spatial_Freshness_And_Rearm_Policy.md)
**Depends On:** [TASK-151-02-02](./TASK-151-02-02_Material_Scene_Changes_Mark_Spatial_State_Stale.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Re-arm required spatial checks and expose explicit next actions when the active
guided session is working from stale spatial facts.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Current Code Anchors

- `session_capabilities.py`
  - `_mark_guided_flow_check_completed_dict(...)`
  - `_advance_guided_flow_for_iteration_dict(...)`
- `areas/reference.py`
  - staged compare/iterate flow-advance path
- `visibility_policy.py`
  - `build_visibility_rules(...)`

## Planned Code Shape

```python
if spatial_state_stale and current_step in {"place_secondary_parts", "checkpoint_iterate", "inspect_validate"}:
    flow_state.spatial_refresh_required = True
    flow_state.step_status = "blocked"
    flow_state.required_checks = build_required_checks(...)
    flow_state.allowed_families = ["spatial_context", "reference_context"]
    flow_state.next_actions = ["refresh_spatial_context"]

if flow_state.spatial_refresh_required and all_required_spatial_checks_completed(flow_state):
    flow_state.spatial_refresh_required = False
    flow_state.spatial_state_stale = False
    flow_state.last_spatial_check_version = flow_state.spatial_state_version
    flow_state.allowed_families = build_allowed_families(current_step)
    flow_state.step_status = restore_step_status(current_step)
```

## Detailed Implementation Notes

- do not overload `current_step` for re-arm; keep the semantic step stable and
  add one explicit `spatial_refresh_required` flag
- visibility/search shaping should consult that flag so directly visible tools
  narrow back to the spatial support set while refresh is pending
- completion of the re-armed checks should restore the current step’s normal
  allowed families instead of restarting the whole guided flow from scratch
- compare/iterate/reference payloads that already expose `guided_flow_state`
  should surface the re-armed state without needing extra client inference

## Acceptance Criteria

- stale spatial state can re-block later guided steps
- the re-armed state is machine-readable and explicit
- the runtime can restore the previous step’s build/checkpoint families once
  the refreshed spatial checks complete

## Planned Unit Test Scenarios

- stale `place_secondary_parts` re-arms spatial checks
- stale `inspect_validate` still allows inspection but reintroduces spatial
  refresh in `next_actions`
- visibility/search rules fall back to the spatial-support set while
  `spatial_refresh_required` is true

## Planned E2E / Transport Scenarios

- streamable guided creature session:
  - create body/head
  - transform one of them
  - observe `next_actions=["refresh_spatial_context"]` before continuing
  - re-run spatial checks and observe the prior step regains its normal allowed
    families

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Status / Closeout Note

- this leaf is done only when the server can both re-arm and later clear the
  spatial refresh requirement in one transport-backed session
