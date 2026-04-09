# TASK-151-01-01: Guided Target Scope Fingerprint And Session Model

**Parent:** [TASK-151-01](./TASK-151-01_Target_Bound_Spatial_Check_Validity.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Track one deterministic identity for the active guided target scope so later
spatial checks can be compared against it.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Current Code Anchors

- `session_capabilities.py`
  - `_build_required_checks(...)`
  - `_build_initial_guided_flow_state(...)`
  - `_normalize_guided_flow_state(...)`
- `guided_flow.py`
  - `GuidedFlowStateContract`
  - `GuidedFlowCheckContract`

## Planned Code Shape

```python
class GuidedTargetScopeContract(MCPContract):
    scope_kind: str
    primary_target: str | None = None
    object_names: list[str] = []
    collection_name: str | None = None


class GuidedFlowStateContract(MCPContract):
    ...
    active_target_scope: GuidedTargetScopeContract | None = None
    spatial_scope_fingerprint: str | None = None

def _normalize_guided_target_scope(...): ...
def _build_guided_target_scope_fingerprint(...): ...
```

## Detailed Implementation Notes

- the fingerprint should be deterministic across equivalent calls:
  - normalize object-name order
  - include `scope_kind`
  - include `primary_target`
  - include `collection_name` when relevant
- prefer a compact guided-scope contract local to `guided_flow.py` instead of
  pulling the full scene graph payload into session state
- the active target scope should be visible on `guided_flow_state` so later
  blocked responses and docs can explain what the spatial checks are actually
  about

## Acceptance Criteria

- the active guided target scope has one deterministic fingerprint
- the fingerprint survives session round-trips and is visible on
  `guided_flow_state`
- `guided_flow_state.active_target_scope` is explicit enough for later
  troubleshooting and transport assertions

## Planned Unit Test Scenarios

- same target-object set with different input order produces the same
  fingerprint
- changing the primary target changes the fingerprint when scope identity has
  materially changed
- unrelated object set produces a different fingerprint
- flow state round-trips the fingerprint cleanly

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Status / Closeout Note

- this leaf is done only when downstream leaves can consume the fingerprint
  instead of recomputing ad-hoc scope identity from raw request arguments
