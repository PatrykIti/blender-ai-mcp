# TASK-162-01: Guided Hidden-Tool Error Classification And Recovery Hints

**Parent:** [TASK-162](./TASK-162_Guided_Hidden_Tool_Error_Semantics_And_Recovery_Clarity.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Replace generic guided `Unknown tool` proxy failures on the `call_tool(...)` seam with deterministic hidden-tool / stale-context recovery semantics when the server knows the active flow step and required spatial checks, then keep direct-call parity explicit in the family-level proof.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/session_capabilities_flow.py`
- `server/adapters/mcp/session_capabilities_state.py`
- `server/adapters/mcp/session_capabilities_bootstrap.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Implementation Notes

- keep `call_tool(...)` strict: hidden tools remain uncallable
- before raising the final proxy error, inspect the active guided state and the
  visible-tool set for the current request
- distinguish at least:
  - truly unknown canonical public tool name
  - known tool hidden by current guided visibility
  - known tool hidden because `spatial_refresh_required` narrowed the allowed
    families
- when the stale-context path is active, point the client at the current
  pending `required_checks` from guided state instead of hard-coding one static
  list of spatial tools
- keep the response compatible with existing `ToolError` handling, but make the
  message deterministic enough that clients do not narrate it as disconnect

## Pseudocode

```python
visible_tools = await transform._get_visible_tools(ctx)
visible_names = {tool.name for tool in visible_tools}
entry = transform._entry_map.get(resolved_name)
session = await get_session_capability_state_async(ctx)
guided_flow = session.guided_flow_state or {}
required_checks = [
    item.get("tool_name")
    for item in guided_flow.get("required_checks") or []
    if isinstance(item, dict) and str(item.get("status") or "") != "completed"
]

if entry is None:
    raise ToolError(unknown_tool_message(resolved_name))

if resolved_name not in visible_names:
    if bool(guided_flow.get("spatial_refresh_required")):
        raise ToolError(
            hidden_due_to_spatial_refresh_message(
                resolved_name,
                required_checks=required_checks,
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

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  This file must be extended with a synthetic Streamable HTTP `call_tool(...)`
  hidden-tool case; the current direct `modeling_transform_object(...)` failure
  lane is not enough for this leaf’s proxy-seam claim.
  `tests/unit/adapters/mcp/test_public_surface_docs.py` must also gain a direct
  assertion for `_docs/_PROMPTS/GUIDED_SESSION_START.md`; grep-only auditing is
  not enough for this named docs surface.

The named tests should explicitly prove all three classifications:

- a truly unknown tool name stays an unknown-tool/discovery error
- internal names, guessed aliases, or non-canonical names that are not valid
  public tool ids remain ordinary unknown-tool cases; the hidden-tool
  classifier applies only after canonical public-name lookup succeeds
- a known tool hidden by guided visibility is surfaced as hidden, not guessed as
  missing
- a known tool hidden because `spatial_refresh_required` is active points to the
  current pending `required_checks`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`
- inherit any additional umbrella docs if the final error wording changes
  cross-surface examples

## Changelog Impact

- include in the parent `TASK-162` changelog entry when shipped

## Validation Commands

- `git diff --check`
- `# Keep this grep as a supplemental audit, but extend test_public_surface_docs.py so _docs/_PROMPTS/GUIDED_SESSION_START.md is asserted directly.`
- `rg -n "Unknown tool|search_tools\\(\\.\\.\\.\\)|call_tool\\(\\.\\.\\.\\)|required_checks" README.md _docs/_MCP_SERVER/README.md _docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_PROMPTS/README.md _docs/_PROMPTS/GUIDED_SESSION_START.md _docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run python scripts/run_e2e_tests.py`
- `poetry run pytest ./tests/unit`

## Acceptance Criteria

- a client asking through `call_tool(...)` for a known-but-hidden guided tool
  gets a recovery-oriented error, not a plain unknown-tool message
- a truly nonexistent tool name remains distinguishable from a known-but-hidden
  tool and does not get reclassified as a guided refresh failure
- when spatial refresh is the cause, the error points to the current pending
  `required_checks` rather than one hard-coded list
- healthy tool-contract failures on the repo-owned proxy/discovery seam now have
  deterministic error semantics; the named proof lanes must make clear which
  transports prove wording and which also prove post-failure continuity

## Status / Board Update

- active child under open parent `TASK-162`; no separate board row
