# TASK-151-01: Target-Bound Spatial Check Validity

**Parent:** [TASK-151](./TASK-151_Spatial_Check_Freshness_Target_Binding_And_Guided_Rearm.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Ensure that required spatial checks are satisfied only when they describe the
active guided target scope, not just any object that happens to exist.

## Current Code Baseline

At the moment the scope gate is completed solely by calling the right tool
name:

- `scene_scope_graph(...)`
- `scene_relation_graph(...)`
- `scene_view_diagnostics(...)`

Each of those tools records completion through
`record_guided_flow_spatial_check_completion(...)`, and the session helper only
checks `tool_name`, not whether the payload matched the active guided target.
That is the exact spoofing hole this subtask closes.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Acceptance Criteria

- `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
  `scene_view_diagnostics(...)` only complete the active required check when
  their scope matches the guided target scope
- unrelated objects such as `Camera` cannot satisfy the required spatial gate
- `guided_flow_state` can explain which target scope the required checks apply to

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-151-01-01](./TASK-151-01-01_Guided_Target_Scope_Fingerprint_And_Session_Model.md) | Store a deterministic fingerprint of the active guided target scope in session state / flow state |
| 2 | [TASK-151-01-02](./TASK-151-01-02_Scene_Spatial_Checks_Must_Match_Active_Target_Scope.md) | Make spatial-check completion conditional on matching the active guided scope |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Detailed Implementation Notes

- the target-bound contract should be flow-level, not repeated independently on
  every required check item
- the scene tools should still return their normal read-only payloads even when
  the scope does not satisfy the active guided gate; only the gate-completion
  side effect should be withheld
- the operator-visible explanation belongs in TASK-151-03-02, but this subtask
  must define the exact runtime fields that docs will describe

## Status / Closeout Note

- do not close this subtask until:
  - the active target-scope identity is exposed on `guided_flow_state`
  - unrelated scopes can no longer complete the spatial gate in transport tests
