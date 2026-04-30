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
- Handoff-driven sculpt visibility must not land without the matching guided
  execution gate. If any `sculpt_*` tool becomes visible on `llm-guided`, the
  bounded sculpt subset must resolve through `GUIDED_TOOL_FAMILY_MAP` /
  `GuidedFlowFamilyLiteral`, or unmapped `sculpt_*` mutators must fail closed in
  `router_helper.py`.

## Runtime / Security Contract

- Visibility level: planner detail is hidden by default and exposed only through
  compact reference-stage fields or opt-in/read-only detail surfaces; sculpt
  tools stay hidden unless a validated handoff explicitly unlocks the bounded
  deterministic subset.
- Behavior: planner detail and discovery artifacts are read-only; any visible
  `sculpt_*` tool is mutating and must be covered by guided execution policy
  before exposure.
- Session/auth assumptions: stdio and Streamable HTTP must derive visibility
  from the same session `guided_handoff` / `guided_flow_state`; local Blender RPC
  remains behind the existing server/addon connection and is not a public auth
  boundary for clients.
- Validation: visibility-relevant handoff fields must be schema-normalized,
  reject unsupported families/tools, and avoid caller-supplied role/family
  spoofing.
- Side effects and recovery: visibility changes should apply in the active MCP
  request path; stale visibility must be recoverable through `router_get_status`
  or the existing visibility refresh path, not a second catalog state.
- Limits and redaction: planner delivery must stay bounded by compact/rich
  payload controls; logs and debug payloads should not include provider secrets,
  local file contents beyond configured artifact references, or unbounded
  captured image data.

## Pseudocode

```python
stage_result = reference_iterate_stage_checkpoint(ctx, preset_profile="compact")
session_state = await get_session_capability_state_async(ctx)

# If stage_result.refinement_handoff needs to affect native visibility, persist
# only the bounded visibility facts through the existing guided_handoff /
# guided_flow_state path before applying visibility.
# Sculpt unlock is allowed only after the same tool subset is mapped/enforced by
# guided execution policy.
rules = build_visibility_rules(
    surface_profile=session_state.surface_profile or "llm-guided",
    phase=session_state.phase,
    guided_handoff=session_state.guided_handoff,
    guided_flow_state=session_state.guided_flow_state,
)
await apply_visibility_for_session_state(ctx, session_state)
```

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/router_helper.py`
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
- handoff-driven sculpt visibility is blocked unless the bounded sculpt subset
  is also governed by guided execution family mapping or fail-closed mutator
  enforcement
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
- Targeted unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_search_surface.py -q`
- Add or update one integration-style scenario when handoff state affects
  native MCP tool visibility for Streamable HTTP / stdio clients.
- Targeted integration lane:
  `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- Docs/preflight:
  `git diff --check`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
