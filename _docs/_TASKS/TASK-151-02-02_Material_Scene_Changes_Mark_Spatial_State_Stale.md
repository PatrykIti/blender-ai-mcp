# TASK-151-02-02: Material Scene Changes Mark Spatial State Stale

**Parent:** [TASK-151-02](./TASK-151-02_Spatial_Freshness_And_Rearm_Policy.md)
**Depends On:** [TASK-151-02-01](./TASK-151-02-01_Spatial_Freshness_Flags_And_Versions_In_Session_State.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Increment the spatial version and mark the spatial layer stale after material
scene changes.

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/modeling.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Current Code Anchors

- `router_helper.py`
  - `route_tool_call_report(...)`
  - `route_tool_call(...)`
- `areas/scene.py`
  - `scene_clean_scene(...)`
  - `macro_align_part_with_contact(...)`
  - `macro_cleanup_part_intersections(...)`
- `areas/modeling.py`
  - `_modeling_create_primitive_impl(...)`
  - `_modeling_transform_object_impl(...)`

## Planned Code Shape

```python
report = route_tool_call_report(...)

if report.error is None and executed_tool_mutates_guided_spatial_state(report):
    mark_guided_spatial_state_stale(
        current_ctx,
        tool_name=report.steps[-1].tool_name,
        family=report.context.guided_tool_family,
        reason=...
    )
```

## Detailed Implementation Notes

- prefer one shared mutation helper called from the routed execution path rather
  than sprinkling stale writes across every individual tool wrapper
- the first invalidation set should be explicit and small:
  - `scene_clean_scene`
  - `modeling_create_primitive`
  - `modeling_transform_object`
  - bounded attachment/alignment cleanup macros that materially move geometry
- read-only tools and blocked/failed executions must not mark the spatial layer
  stale
- if one routed call expands into a sequence, stale marking should use the
  final successful effective tool / family rather than the original user tool
  name only

## Acceptance Criteria

- scene reset, primitive creation, transforms, and selected macro edits dirty
  the spatial state
- pure read-only checks do not dirty it

## Planned Unit Test Scenarios

- `scene_clean_scene(...)` marks spatial state stale
- `modeling_create_primitive(...)` marks spatial state stale
- `modeling_transform_object(...)` marks spatial state stale
- `macro_align_part_with_contact(...)` marks spatial state stale when it
  succeeds
- `scene_scope_graph(...)` does not dirty the spatial state
- blocked guided execution does not dirty the spatial state

## Planned E2E / Transport Scenarios

- same-session guided creature transport flow:
  - unlock build
  - create or transform a registered part
  - confirm `router_get_status().guided_flow_state.spatial_state_stale == true`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Status / Closeout Note

- completed on 2026-04-09 after unit and transport coverage proved that real
  guided scene mutations dirty the spatial layer in-session

## Completion Summary

- routed guided execution now marks spatial state stale after successful scene
  resets, primitive creation/transform, and bounded attachment/alignment
  mutations
- blocked/failed calls and read-only spatial checks do not dirty the spatial
  layer
