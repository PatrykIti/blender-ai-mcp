# TASK-149-01: Visibility Policy And Guided Handoff Default Spatial Support

**Parent:** [TASK-149](./TASK-149_Guided_Default_Spatial_Graph_And_View_Diagnostics_For_All_Goal_Oriented_Sessions.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
`scene_view_diagnostics(...)` directly visible on all active goal-oriented
`llm-guided` phases and typed handoff contracts.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/router.py`

## Acceptance Criteria

- spatial graph/view helpers are part of the default visible guided support
  set after `router_set_goal(...)`
- creature blockout recipes no longer hide those helpers behind supporting-only
  metadata while leaving them unavailable in practice
- the same tools remain off no-goal bootstrap unless a separate policy change
  explicitly widens bootstrap
- `router_get_status(...)` visibility diagnostics reflect the new behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped
