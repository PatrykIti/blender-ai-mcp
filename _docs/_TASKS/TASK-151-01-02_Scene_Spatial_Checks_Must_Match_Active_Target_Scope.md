# TASK-151-01-02: Scene Spatial Checks Must Match Active Target Scope

**Parent:** [TASK-151-01](./TASK-151-01_Target_Bound_Spatial_Check_Validity.md)
**Depends On:** [TASK-151-01-01](./TASK-151-01-01_Guided_Target_Scope_Fingerprint_And_Session_Model.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make spatial-check completion in `scene_*` depend on the active guided target
scope instead of whatever object the model happens to pass.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Current Code Anchors

- `scene.py`
  - `scene_scope_graph(...)`
  - `scene_relation_graph(...)`
  - `scene_view_diagnostics(...)`
- `session_capabilities.py`
  - `record_guided_flow_spatial_check_completion(...)`
  - `_mark_guided_flow_check_completed_dict(...)`

## Planned Code Shape

```python
resolved_scope = normalize_scope_from_payload(...)

if not guided_scope_matches_active_session_scope(resolved_scope, current_flow_state):
    return payload_without_completing_required_check(...)

record_guided_flow_spatial_check_completion(
    ctx,
    tool_name="scene_view_diagnostics",
    resolved_scope=resolved_scope,
    scope_fingerprint=resolved_fingerprint,
)
```

## Detailed Implementation Notes

- the scene tools should continue to succeed as read-only inspection tools even
  when the active guided gate is not satisfied
- only the state mutation should be conditional on scope match
- `scene_view_diagnostics(target_object="Camera")` should remain a legal
  inspection call; it just must not advance a creature/building flow whose
  active target scope is `Head`/`Body`
- matching should compare normalized guided scope identity, not raw argument
  shape, so equivalent object-set calls still count

## Acceptance Criteria

- `scene_view_diagnostics(target_object="Camera")` does not satisfy the
  creature/building spatial gate unless that camera is actually the active
  guided target
- spatial checks on the real target scope still complete normally

## Planned Unit Test Scenarios

- matching scope completes the required check
- non-matching scope returns payload but does not complete the required check
- empty scene / unrelated camera path cannot spoof the required gate

## Planned E2E / Transport Scenarios

- streamable guided creature session:
  - `scene_view_diagnostics(target_object="Camera")` leaves the gate pending
  - `scene_view_diagnostics(target_object="Head", target_objects=["Body"])`
    still completes the pending guided check

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Status / Closeout Note

- completed on 2026-04-09 after stdio/streamable regressions proved that an
  unrelated helper scope cannot spoof the guided spatial gate

## Completion Summary

- `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
  `scene_view_diagnostics(...)` now pass normalized target scope identity into
  the guided flow helper
- unrelated scopes return normal read-only payloads but no longer complete the
  active guided spatial check
