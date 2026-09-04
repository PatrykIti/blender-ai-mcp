# TASK-150-05-01: Unit And Transport Regression Matrix For Flow State And Gating

**Parent:** [TASK-150-05](./TASK-150-05_Regression_Pack_And_Docs_For_Server_Driven_Guided_Flows.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Build the regression matrix for the new server-driven guided flow layer across
unit and transport-backed scenarios.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/`
- `tests/e2e/router/`

## Planned File Work

- Modify:
  - `tests/unit/adapters/mcp/test_router_elicitation.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
  - `tests/unit/adapters/mcp/test_guided_mode.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
  - `tests/e2e/router/test_guided_manual_handoff.py`
- Create:
  - `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
  - `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
  - `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
  - `tests/e2e/integration/test_guided_flow_step_gating.py`
  - `tests/e2e/integration/test_guided_streamable_flow_step_gating.py`
  - `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`

## Acceptance Criteria

- unit tests prove flow-state transitions and step-aware visibility
- transport-backed tests prove same-session behavior on stdio and streamable
- regressions cover at least one `generic`, one `creature`, and one
  `building`-profile scenario or an explicit placeholder path for the latter

## Pseudocode Sketch

```python
def test_creature_flow_starts_in_establish_spatial_context():
    result = router_set_goal(...)
    assert result.guided_flow_state.domain_profile == "creature"
    assert result.guided_flow_state.current_step == "establish_spatial_context"

def test_build_tools_stay_blocked_until_required_checks_complete():
    ...
```

## Planned Test Matrix

### Unit

- `test_guided_flow_state_contract.py`
  - contract field names
  - enum vocabulary
  - session serialization / deserialization
- `test_guided_flow_domain_profiles.py`
  - generic profile selection
  - creature profile selection
  - building profile selection
  - fallback behavior
- `test_router_elicitation.py`
  - `router_set_goal(...)` emits `guided_flow_state`
  - `router_get_status()` returns the same flow state
  - blocked families produce structured guidance
- `test_visibility_policy.py`
  - flow-step-aware visibility matrix
- `test_guided_mode.py`
  - visibility diagnostics include flow-driven rule changes
- `test_search_surface.py`
  - search results stay aligned with step gating
- `test_prompt_provider_flow_bundles.py`
  - required/preferred prompt bundle exposure
- `test_prompt_catalog_flow_mapping.py`
  - flow/domain/step prompt mapping

### E2E / Transport

- `test_guided_flow_step_gating.py`
  - stdio same-session flow progression
  - blocked later-stage family before required checks
  - required checks unlock next family
- `test_guided_streamable_flow_step_gating.py`
  - same as above over `streamable-http`
  - reconnect/new-session reset semantics for flow step
- `test_guided_flow_step_gating_router_paths.py`
  - `no_match` / `guided_manual_build`
  - workflow-ready path
  - both produce coherent step-gated behavior

## Example E2E Assertions

```python
assert status["guided_flow_state"]["domain_profile"] == "creature"
assert status["guided_flow_state"]["current_step"] == "establish_spatial_context"
assert "macro_finish_form" not in current_tools
assert "scene_scope_graph" in current_tools
assert blocked_payload["guided_flow_state"]["step_status"] == "blocked"
assert "run_required_checks" in blocked_payload["guided_flow_state"]["next_actions"]
```

## Docs To Update

- none directly; this slice is primarily for regression coverage

## Tests To Add/Update

- the files listed in Repository Touchpoints plus the new files above

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped

## Completion Summary

- unit coverage now proves flow-state transitions, role summaries, and
  visibility/search parity
- transport-backed coverage now proves same-session role registration and
  family/role enforcement on stdio/streamable harnesses
