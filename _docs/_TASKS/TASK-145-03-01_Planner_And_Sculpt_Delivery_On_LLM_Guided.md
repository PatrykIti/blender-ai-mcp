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
- `ReferenceRefinementHandoffContract` is currently carried by reference
  compare / iterate responses. If this task makes handoff state affect native
  visibility, normalize the visibility-relevant subset into existing
  `guided_handoff` or `guided_flow_state` instead of introducing a second
  planner-state catalog.

## Pseudocode

```python
stage_result = reference_iterate_stage_checkpoint(ctx, preset_profile="compact")
session_state = get_session_capability_state(ctx)

# If stage_result.refinement_handoff needs to affect native visibility, persist
# only the bounded visibility facts through the existing guided_handoff /
# guided_flow_state path before applying visibility.
rules = build_visibility_rules(
    surface_profile="llm-guided",
    phase=current_guided_phase(ctx),
    guided_handoff=session_state.guided_handoff,
    guided_flow_state=session_state.guided_flow_state,
)
await apply_session_visibility(
    ctx,
    surface_profile="llm-guided",
    phase=current_guided_phase(ctx),
    guided_handoff=session_state.guided_handoff,
    guided_flow_state=session_state.guided_flow_state,
)
```

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Acceptance Criteria

- no broad new planner/sculpt family becomes bootstrap-visible by default
- any planner or sculpt-context delivery path stays phase-aware and
  goal-aware
- search / visibility policy can surface the right bounded artifact when the
  current handoff justifies it
- native MCP `list_tools()` / search visibility refreshes when planner or
  handoff state changes
- handoff-driven visibility, if implemented, uses the existing
  `guided_handoff` / `guided_flow_state` inputs to `build_visibility_rules(...)`
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
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Validation Category

- Unit tests must cover static policy and active guided-state visibility
  refresh.
- Add or update one integration-style scenario when handoff state affects
  native MCP tool visibility for Streamable HTTP / stdio clients.
- Targeted integration lane:
  `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_surface_contract_parity.py -q`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
