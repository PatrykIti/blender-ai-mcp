# TASK-145-03-01: Planner and Sculpt Delivery On `llm-guided`

**Parent:** [TASK-145-03](./TASK-145-03_Guided_Adoption_Visibility_Docs_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-03](./TASK-145-01-03_Planner_Summary_Placement_And_Compare_Iterate_Budget_Gates.md), [TASK-145-02-03](./TASK-145-02-03_Bounded_Sculpt_Metadata_And_Recommendation_Policy.md)

## Objective

Define the public-surface delivery model for planner and sculpt-context
artifacts on `llm-guided` so they stay:

- bounded
- discoverable when justified
- hidden when they would bloat bootstrap or generic build paths

## Implementation Notes

- Any planner/sculpt visibility change must go through the existing visibility
  policy and guided mode surfaces. Do not add a parallel catalog-shaping
  mechanism.
- If planner or handoff state changes the visible tool set for native MCP
  clients, refresh/apply visibility in the active request path so
  `list_tools()` and search do not stay stale.
- Delivery should prefer compact fields on the existing reference stage
  response plus bounded search/discovery hints. Avoid a broad bootstrap-visible
  planner or sculpt family.
- Streamable HTTP and stdio clients should see the same truthful bounded
  visibility semantics.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Acceptance Criteria

- no broad new planner/sculpt family becomes bootstrap-visible by default
- any planner or sculpt-context delivery path stays phase-aware and
  goal-aware
- search / visibility policy can surface the right bounded artifact when the
  current handoff justifies it
- native MCP `list_tools()` / search visibility refreshes when planner or
  handoff state changes
- default build and inspect phase footprints remain materially below the broad
  legacy catalog

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Validation Category

- Unit tests must cover static policy and active guided-state visibility
  refresh.
- Add or update one integration-style scenario when handoff state affects
  native MCP tool visibility for Streamable HTTP / stdio clients.

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
