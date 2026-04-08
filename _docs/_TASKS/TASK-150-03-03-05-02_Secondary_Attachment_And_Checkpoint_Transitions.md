# TASK-150-03-03-05-02: Secondary, Attachment, And Checkpoint Transitions

**Parent:** [TASK-150-03-03-05](./TASK-150-03-03-05_Flow_Transitions_From_Role_Groups_And_Checkpoints.md)
**Depends On:** [TASK-150-03-03-05-01](./TASK-150-03-03-05-01_Primary_Mass_Role_Group_Completion_Rules.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Advance later guided steps from secondary-role completion and compare/iterate
checkpoint outcomes.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/reference.py`

## Current Code Anchors

- `session_capabilities.py` lines 1117-1149: current checkpoint/iterate transitions
- `areas/reference.py` staged compare/iterate flow-advance call sites

## Planned Code Shape

```python
if current_step == "place_secondary_parts" and required_secondary_roles_present(...):
    current_step = "checkpoint_iterate"

if loop_disposition == "inspect_validate":
    current_step = "inspect_validate"
elif loop_disposition == "stop":
    current_step = "finish_or_stop"
```

## Acceptance Criteria

- secondary-part completion can unlock checkpoint iteration
- checkpoint outcomes still drive inspect/finish transitions

## Planned Unit Test Scenarios

- `ear_pair + foreleg_pair + hindleg_pair` advance a creature flow into
  `checkpoint_iterate`
- `loop_disposition="inspect_validate"` overrides family unlock and moves the
  flow into inspection
- `loop_disposition="stop"` moves the flow into `finish_or_stop`

## Planned E2E / Transport Scenarios

- guided creature compare/iterate loop:
  - complete secondary parts
  - run checkpoint iterate
  - verify inspect/finish transition semantics

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
