# TASK-150-03-03-05-01: Primary Mass Role Group Completion Rules

**Parent:** [TASK-150-03-03-05](./TASK-150-03-03-05_Flow_Transitions_From_Role_Groups_And_Checkpoints.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Advance out of `create_primary_masses` when the required primary role groups
exist for the active overlay.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`

## Current Code Anchors

- lines 1012-1018: current transition into `create_primary_masses`
- lines 1107-1149: current later transitions

## Planned Code Shape

```python
if current_step == "create_primary_masses" and required_primary_roles_present(registry, overlay):
    contract.completed_steps.append("create_primary_masses")
    contract.current_step = "place_secondary_parts"
    contract.required_role_groups = ["ear_pair", "foreleg_pair", "hindleg_pair"]
```

## Acceptance Criteria

- role groups, not just spatial checks, can drive the next step transition

## Planned Unit Test Scenarios

- `body_core + head_mass` complete the primary group for `creature`
- `main_volume` completes the primary group for `building` when that is the
  declared overlay rule
- duplicate role registration does not re-advance the same step twice

## Planned E2E / Transport Scenarios

- guided creature session:
  - after registering `body_core` only, step stays `create_primary_masses`
  - after registering `head_mass`, step advances

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
