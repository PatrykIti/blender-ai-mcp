# TASK-150-03-03-05: Flow Transitions From Role Groups And Checkpoints

**Parent:** [TASK-150-03-03](./TASK-150-03-03_Generic_Families_Part_Roles_And_Execution_Enforcement.md)
**Depends On:** [TASK-150-03-03-02](./TASK-150-03-03-02_Guided_Part_Role_Registry_And_Session_Contracts.md), [TASK-150-03-03-04](./TASK-150-03-03-04_Router_Execution_Guards_And_Blocked_Response_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Advance guided steps from completed role groups and checkpoint outcomes instead
of relying only on spatial-context completion.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `tests/unit/adapters/mcp/`

## Acceptance Criteria

- `create_primary_masses` can complete when the required primary role groups
  exist for the active overlay
- `place_secondary_parts` can complete when the required secondary role groups
  exist for the active overlay
- checkpoint/iterate outputs can move the flow into:
  - `checkpoint_iterate`
  - `inspect_validate`
  - `finish_or_stop`
- transitions remain machine-readable and explainable through
  `guided_flow_state`

## Detailed Implementation Notes

- keep current spatial-context completion logic; extend it, do not replace it
- overlay-specific role-group requirements should remain declarative where
  possible
- likely examples:
  - creature primary masses:
    - `body_core`
    - `head_mass`
    - optional or required `tail_mass`
  - creature secondary parts:
    - `ear_pair`
    - `foreleg_pair`
    - `hindleg_pair`
    - optional `snout_mass`

## Current Code Anchors

- `server/adapters/mcp/session_capabilities.py`
  - lines 252-314: initial flow-state construction
  - lines 993-1026: spatial-check completion and `create_primary_masses` transition
  - lines 1107-1149: iterate-based transitions
- `server/adapters/mcp/areas/reference.py`
  - lines around staged compare/iterate response construction and flow advancement

## Pseudocode Sketch

```python
if current_step == "create_primary_masses" and role_groups_complete(
    required=("body_core", "head_mass"),
    registry=part_registry,
):
    flow_state.current_step = "place_secondary_parts"
    flow_state.required_role_groups = ["ear_pair", "foreleg_pair", "hindleg_pair"]

if current_step == "place_secondary_parts" and role_groups_complete(...):
    flow_state.current_step = "checkpoint_iterate"
```

## Planned Unit Test Scenarios

- registering required primary role groups advances the flow into
  `place_secondary_parts`
- secondary role groups advance into `checkpoint_iterate`
- iterate-loop outcomes still move the flow into `inspect_validate` and
  `finish_or_stop`

## Planned E2E / Transport Scenarios

- creature stdio session:
  - register primary masses
  - verify step transition
  - register secondary parts
  - verify checkpoint transition
- transport-backed iterate loop:
  - after checkpoint result, flow transitions to `inspect_validate`

## Execution Structure

| Order | Micro-Leaf | Purpose |
|------|------------|---------|
| 1 | [TASK-150-03-03-05-01](./TASK-150-03-03-05-01_Primary_Mass_Role_Group_Completion_Rules.md) | Advance out of `create_primary_masses` when the required primary role groups exist |
| 2 | [TASK-150-03-03-05-02](./TASK-150-03-03-05-02_Secondary_Attachment_And_Checkpoint_Transitions.md) | Advance secondary/attachment/checkpoint steps from role groups plus compare/iterate outcomes |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`

## Changelog Impact

- include in the parent TASK-150 execution-enforcement changelog entry

## Completion Summary

- spatial-context completion still unlocks `create_primary_masses`
- required primary roles now unlock `place_secondary_parts`
- required secondary roles now unlock `checkpoint_iterate`
- existing iterate-loop outcomes continue to own the later
  `inspect_validate` / `finish_or_stop` transitions
