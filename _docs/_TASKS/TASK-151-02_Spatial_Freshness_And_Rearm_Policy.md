# TASK-151-02: Spatial Freshness And Re-Arm Policy

**Parent:** [TASK-151](./TASK-151_Spatial_Check_Freshness_Target_Binding_And_Guided_Rearm.md)
**Depends On:** [TASK-151-01](./TASK-151-01_Target_Bound_Spatial_Check_Validity.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Track when spatial facts become stale and re-arm the required spatial layer
after material scene changes instead of treating spatial checks as a one-time
bootstrap ritual.

## Current Code Baseline

The current flow contract still treats spatial checks as first-use-only:

- `record_guided_flow_spatial_check_completion(...)` can move
  `establish_spatial_context -> create_primary_masses`
- after that transition there is no version/freshness comparison between:
  - the last validated spatial state
  - later scene-changing edits
- `route_tool_call_report(...)` already knows the effective tool/family/role
  for successful executions, so it is the natural centralized hook for marking
  the spatial layer stale
- `build_visibility_rules(...)` currently narrows visibility mainly from
  `current_step`, so a stale-spatial re-arm path needs one explicit flow-state
  flag instead of relying only on prompt hints

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Acceptance Criteria

- the runtime can mark the spatial layer stale after material scene changes
- guided flow can explicitly require a spatial refresh before continuing
- later-stage calls can surface `next_actions` such as `refresh_spatial_context`
  instead of silently trusting stale scope/relation/view facts

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-151-02-01](./TASK-151-02-01_Spatial_Freshness_Flags_And_Versions_In_Session_State.md) | Add freshness/version bookkeeping for the spatial layer |
| 2 | [TASK-151-02-02](./TASK-151-02-02_Material_Scene_Changes_Mark_Spatial_State_Stale.md) | Mark the spatial layer stale after scene resets, primitive creation, transforms, and selected macro edits |
| 3 | [TASK-151-02-03](./TASK-151-02-03_Guided_Flow_Rearms_Spatial_Checks_After_Stale_Changes.md) | Re-arm spatial checks and next actions when the spatial layer has become stale |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Detailed Implementation Notes

- freshness bookkeeping should stay deterministic and cheap:
  simple counters / booleans in session state, not scene-hash speculation
- invalidation should happen only after successful scene-changing executions;
  blocked or failed calls must not dirty spatial state
- re-arm should not require rewinding the whole guided flow back to
  `establish_spatial_context`; a cleaner first slice is:
  - keep the semantic step (`place_secondary_parts`, `checkpoint_iterate`,
    `inspect_validate`, ...)
  - set a machine-readable `spatial_refresh_required` flag
  - temporarily narrow visibility / allowed families until the required checks
    are refreshed again

## Status / Closeout Note

- closed on 2026-04-09 once stale-spatial behavior became visible through
  `router_get_status().guided_flow_state` and transport-backed guided sessions
  could re-arm/clear the spatial refresh requirement

## Completion Summary

- added explicit spatial freshness/version fields to `guided_flow_state`
- successful guided scene mutations can now stale the spatial layer
- guided flows can now re-arm and later clear `refresh_spatial_context`
  without rewinding the semantic step name
