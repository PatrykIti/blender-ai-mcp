# TASK-149-01: Visibility Policy And Guided Handoff Default Spatial Support

**Parent:** [TASK-149](./TASK-149_Guided_Default_Spatial_Graph_And_View_Diagnostics_For_All_Goal_Oriented_Sessions.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
`scene_view_diagnostics(...)` directly visible on `llm-guided`, including
bootstrap and all active guided phases plus typed handoff contracts.

**Completion Summary:** Completed on 2026-04-08. The `llm-guided` visibility
policy now keeps the spatial graph/view helpers enabled as default guided
support tools, and the scene capability pins them into the shaped direct tool
surface so `tools/list` clients can actually see them instead of depending on
phase-local hidden visibility only.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/router.py`

## Acceptance Criteria

- spatial graph/view helpers are part of the default visible guided support
  set on `llm-guided`
- creature blockout recipes no longer hide those helpers behind supporting-only
  metadata while leaving them unavailable in practice
- `router_get_status(...)` visibility diagnostics reflect the new behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped
