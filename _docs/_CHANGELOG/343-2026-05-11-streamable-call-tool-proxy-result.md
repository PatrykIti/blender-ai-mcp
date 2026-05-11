# 343. Streamable call_tool proxy result unwrap

Date: 2026-05-11
Task: Runtime guided-surface follow-up

## Summary

- Updated the synthetic `call_tool(...)` proxy to return a plain
  `{"result": ...}` payload built from the proxied FastMCP tool result instead
  of returning the nested `ToolResult` object directly.
- Preserved the existing public response shape while avoiding Streamable HTTP
  client stalls or empty structured payloads after a proxied utility call such
  as `collection_manage(...)`.
- Added a Streamable HTTP regression that executes
  `call_tool(name="collection_manage", arguments=...)` during the guided
  creature build phase.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py::test_call_tool_proxy_matches_direct_public_alias_execution tests/unit/adapters/mcp/test_search_surface.py::test_call_tool_can_canonicalize_collection_manage_name_alias -q`
  (`2 passed`)
- `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py::test_streamable_guided_session_expands_visible_tools_after_goal_handoff -q`
  (`1 passed`)
