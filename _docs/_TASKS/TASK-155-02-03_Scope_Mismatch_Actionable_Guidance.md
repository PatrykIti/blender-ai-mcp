# TASK-155-02-03: Scope Mismatch Actionable Guidance

**Parent:** [TASK-155-02](./TASK-155-02_Governor_Workset_Refresh_And_Bootstrap_Discipline.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make spatial-refresh tools return clear guided feedback when the caller switches
scope mid-gate, for example `scene_scope_graph(Head, Ear_L)` followed by
`scene_relation_graph(Body, Tail)`.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/application/services/spatial_graph.py`
- `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`

## Acceptance Criteria

- mismatched `scene_relation_graph(...)` and `scene_view_diagnostics(...)`
  calls remain read-only but explicitly say they did not satisfy the active
  guided scope
- the response includes the active scope and the expected rerun target shape
- matching scope still completes the relevant required spatial check
- the model no longer has to infer failure from unchanged `router_get_status()`
  alone

## Tests To Add/Update

- Unit:
  - add active-scope mismatch cases to
    `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
  - add flow-state persistence checks in
    `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- E2E:
  - extend `tests/e2e/integration/test_guided_streamable_spatial_support.py`
    with mismatched spatial refresh scope and expected actionable message

## Changelog Impact

- include in the TASK-155 changelog entry

## Completion Summary

- relation/view spatial reads now report when they are read-only but do not
  satisfy the active guided refresh scope
