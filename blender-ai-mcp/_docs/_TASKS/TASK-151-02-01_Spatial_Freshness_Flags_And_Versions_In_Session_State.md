# TASK-151-02-01: Spatial Freshness Flags And Versions In Session State

**Parent:** [TASK-151-02](./TASK-151-02_Spatial_Freshness_And_Rearm_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Add explicit freshness/version bookkeeping for the spatial layer to session
state and `guided_flow_state`.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Current Code Anchors

- `session_capabilities.py`
  - `_build_initial_guided_flow_state(...)`
  - `_mark_guided_flow_check_completed_dict(...)`
  - `_advance_guided_flow_for_iteration_dict(...)`

## Planned Code Shape

```python
class GuidedFlowStateContract(MCPContract):
    ...
    spatial_state_version: int = 0
    spatial_state_stale: bool = False
    last_spatial_check_version: int | None = None
    spatial_refresh_required: bool = False
    last_spatial_mutation_reason: str | None = None
```

## Detailed Implementation Notes

- `spatial_state_version` should represent the latest scene-changing mutation
  that matters for guided spatial truth
- `last_spatial_check_version` should represent the version last validated by
  the completed scope/relation/view diagnostic set
- `spatial_refresh_required` is the machine-readable switch that later leaves
  can use for:
  - visibility narrowing
  - execution narrowing
  - explicit `next_actions=["refresh_spatial_context"]`
- keep the fields on `guided_flow_state` so:
  - `router_get_status()`
  - reference compare/iterate payloads
  - docs/tests
  all see the same freshness model

## Acceptance Criteria

- guided flow carries explicit stale/fresh state for spatial facts
- the server can compare “current scene spatial version” vs “last validated
  spatial version”
- the flow contract can explicitly say “spatial refresh is pending” without
  mutating the semantic step name

## Planned Unit Test Scenarios

- state round-trips the new freshness/version fields
- fresh and stale states serialize distinctly
- payload parity tests include the new guided-flow fields where guided flow is
  already exposed

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Status / Closeout Note

- completed on 2026-04-09; later leaves now mutate and consume these fields in
  runtime logic, transport payloads, and docs

## Completion Summary

- added guided spatial freshness/version fields to `GuidedFlowStateContract`
- exposed those fields through the existing `guided_flow_state` payloads
