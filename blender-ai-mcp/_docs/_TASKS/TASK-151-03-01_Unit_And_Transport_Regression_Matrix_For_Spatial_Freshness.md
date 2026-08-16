# TASK-151-03-01: Unit And Transport Regression Matrix For Spatial Freshness

**Parent:** [TASK-151-03](./TASK-151-03_Regression_And_Docs_For_Spatial_Rearm.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Build the regression matrix for target-bound spatial checks and stale-spatial
re-arm behavior.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Planned Matrix

- unit:
  - `active_target_scope` / fingerprint round-trips on `guided_flow_state`
  - camera/unrelated scope does not satisfy `scene_view_diagnostics` check
  - successful scene mutation increments `spatial_state_version`
  - blocked/failed execution does not dirty spatial state
  - stale flow re-arms required checks and `next_actions`
  - `spatial_refresh_required` narrows visibility/search back to spatial tools
- transport:
  - stdio same-session spoof attempt on `Camera` leaves the gate pending
  - streamable same-session re-arm after primitive creation/transform
  - refreshed spatial checks clear the stale/refresh-required state without
    losing the current semantic step

## Acceptance Criteria

- the server proves ongoing spatial discipline, not just first-use gating

## Docs To Update

- none directly; consume the shipped behavior in
  [TASK-151-03-02](./TASK-151-03-02_Public_Docs_And_Troubleshooting_For_Spatial_Rearm.md)

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Status / Closeout Note

- completed on 2026-04-09 with both unit and transport harness coverage for
  the new target-bound and freshness-aware behavior

## Completion Summary

- added unit regressions for target binding, stale marking, and spatial re-arm
- added transport regressions for spoofed helper scopes and same-session
  refresh behavior on guided stdio/streamable flows
