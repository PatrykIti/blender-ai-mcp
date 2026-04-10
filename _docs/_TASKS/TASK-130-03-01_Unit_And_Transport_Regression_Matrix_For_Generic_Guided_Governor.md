# TASK-130-03-01: Unit And Transport Regression Matrix For Generic Guided Governor

**Parent:** [TASK-130-03](./TASK-130-03_Regression_And_Docs_Closeout_For_Generic_Guided_Governor.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Build the regression matrix proving the generic guided governor stays
disciplined across bootstrap, step progression, target/workset handling, and
search/discovery on both unit and transport-backed sessions.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Planned Validation Matrix

- unit:
  - correct bootstrap/request triage
  - bounded next-actions / step transitions
  - target/workset discipline
  - domain-adaptive progression
  - bounded search/discovery
- transport:
  - stdio same-session guided build
  - streamable same-session guided build
  - generic/object-style fallback path
  - building/facade path

## Pseudocode Sketch

```python
status = router_get_status()
assert status["guided_flow_state"]["next_actions"] == ["run_required_checks"]
assert status["guided_flow_state"]["allowed_families"] == ["spatial_context"]
assert "collection_manage" not in search_results_before_unlock
```

## Acceptance Criteria

- regressions prove the governor story generically, not just for squirrel-like
  sessions

## Changelog Impact

- include in the parent TASK-130 changelog entry

## Completion Summary

- added unit coverage for:
  - explicit guided-scope discipline
  - delayed inspect escalation
  - exact-match / compact search
- reran stdio/streamable parity against the updated governor behavior
