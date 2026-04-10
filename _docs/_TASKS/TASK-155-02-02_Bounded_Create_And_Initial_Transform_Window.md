# TASK-155-02-02: Bounded Create And Initial Transform Window

**Parent:** [TASK-155-02](./TASK-155-02_Governor_Workset_Refresh_And_Bootstrap_Discipline.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Resolve the product contradiction where docs say to create a primitive and then
call `modeling_transform_object(scale=...)`, while the guided surface may hide
that transform immediately because spatial refresh is pending.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- one chosen runtime contract is implemented:
  - allow `modeling_transform_object(...)` for the just-created/registered
    object before the first refresh, or
  - support a bounded create-and-shape action, or
  - document and enforce a different first-class path
- spatial refresh still re-arms after material changes, but does not produce
  avoidable "Unknown tool" loops for the documented initial-shape step
- search/discovery returns the same next action the visible surface supports
- failed or unrelated transforms still do not bypass spatial freshness policy

## Tests To Add/Update

- Unit:
  - `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
  - `tests/unit/adapters/mcp/test_context_bridge.py`
- E2E:
  - extend `tests/e2e/integration/test_guided_surface_contract_parity.py`
    with create -> initial scale -> refresh
  - extend `tests/e2e/integration/test_guided_streamable_spatial_support.py`
    for transport-visible behavior

## Changelog Impact

- include in the TASK-155 changelog entry
