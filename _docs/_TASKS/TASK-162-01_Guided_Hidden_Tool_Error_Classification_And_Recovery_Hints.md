# TASK-162-01: Guided Hidden-Tool Error Classification And Recovery Hints

**Parent:** [TASK-162](./TASK-162_Guided_Hidden_Tool_Error_Semantics_And_Recovery_Clarity.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Replace generic guided `Unknown tool` proxy failures with deterministic hidden-tool / stale-context recovery semantics when the server knows the active flow step and required spatial checks.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/session_capabilities_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Implementation Notes

- keep `call_tool(...)` strict: hidden tools remain uncallable
- before raising the final proxy error, inspect the active guided state and the
  visible-tool set for the current request
- distinguish at least:
  - truly unknown tool name
  - known tool hidden by current guided visibility
  - known tool hidden because `spatial_refresh_required` narrowed the allowed
    families
- when the stale-context path is active, point the client at the exact required
  spatial tools instead of telling it only to use `search_tools(...)`
- keep the response compatible with existing `ToolError` handling, but make the
  message deterministic enough that clients do not narrate it as disconnect

## Pseudocode

```python
visible_tools = await transform._get_visible_tools(ctx)
visible_names = {tool.name for tool in visible_tools}
entry = discovery_entry_map.get(resolved_name)
session = await get_session_capability_state_async(ctx)

if entry is None:
    raise ToolError(unknown_tool_message(resolved_name))

if resolved_name not in visible_names:
    if session.guided_flow_state.spatial_refresh_required:
        raise ToolError(
            hidden_due_to_spatial_refresh_message(
                resolved_name,
                required_checks=["scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"],
            )
        )
    raise ToolError(hidden_due_to_guided_visibility_message(resolved_name))

return await ctx.fastmcp.call_tool(resolved_name, canonical_arguments)
```

## Runtime / Security Contract Notes

- do not list hidden mutating tools beyond the named tool the client already
  asked for
- do not leak stack traces or internal visibility rule dumps
- keep stdio and Streamable HTTP behavior identical for the same guided-state
  cause

## Tests To Add/Update

- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- targeted unit coverage if helper classification logic is extracted

## Docs To Update

- inherit umbrella docs unless the final error wording requires explicit public
  examples

## Changelog Impact

- include in the parent `TASK-162` changelog entry when shipped

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `poetry run pytest ./tests/unit`

## Acceptance Criteria

- a client asking for a known-but-hidden guided tool gets a recovery-oriented
  error, not a plain unknown-tool message
- when spatial refresh is the cause, the error points to
  `scene_scope_graph`, `scene_relation_graph`, and `scene_view_diagnostics`
- healthy tool-contract failures no longer look like transport disconnects in
  the repo-owned surface semantics

## Status / Board Update

- historical child under `TASK-162`; no separate board row
