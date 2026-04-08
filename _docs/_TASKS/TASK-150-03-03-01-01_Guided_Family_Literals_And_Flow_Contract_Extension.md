# TASK-150-03-03-01-01: Guided Family Literals And Flow Contract Extension

**Parent:** [TASK-150-03-03-01](./TASK-150-03-03-01_Shared_Tool_Family_Vocabulary_And_Overlay_Mapping.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Extend the shared guided-flow contract with a stable family vocabulary that can
be reused by `generic`, `creature`, and `building` overlays.

## Repository Touchpoints

- `server/adapters/mcp/contracts/guided_flow.py`

## Current Code Anchors

- lines 12-23: current domain/step/status literals
- lines 36-48: current `GuidedFlowStateContract`

## Planned Code Shape

```python
GuidedFlowFamilyLiteral = Literal[
    "spatial_context",
    "reference_context",
    "primary_masses",
    "secondary_parts",
    "attachment_alignment",
    "checkpoint_iterate",
    "inspect_validate",
    "finish",
    "utility",
]

class GuidedFlowStateContract(MCPContract):
    ...
    allowed_families: list[GuidedFlowFamilyLiteral] = []
```

## Acceptance Criteria

- shared family literals exist in one canonical contract file
- `guided_flow_state` can expose `allowed_families`

## Completion Summary

- added `GuidedFlowFamilyLiteral` to the shared guided-flow contract
- extended `GuidedFlowStateContract` with `allowed_families`
- added unit coverage for:
  - valid `allowed_families`
  - invalid family rejection
  - guided-flow session round-trip with family serialization

## Planned Unit Test Scenarios

- `GuidedFlowStateContract` accepts valid `allowed_families`
- invalid family literals are rejected
- optional family fields still serialize cleanly when empty

## Planned E2E / Transport Scenarios

- not required at this micro-leaf; covered by higher-level family-mapping and
  execution-enforcement transport tests

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
