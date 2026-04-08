# TASK-150-03-03-02-01: Internal Part Registry Session Key And Model

**Parent:** [TASK-150-03-03-02](./TASK-150-03-03-02_Guided_Part_Role_Registry_And_Session_Contracts.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add the internal session key and registry model used to track guided part
roles.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`

## Current Code Anchors

- lines 29-44: current session keys
- lines 95-122: current `SessionCapabilityState`
- lines 317-339: state reads
- lines 388-411: state writes

## Planned Code Shape

```python
SESSION_GUIDED_PART_REGISTRY_KEY = "guided_part_registry"

@dataclass(frozen=True)
class GuidedPartRegistryItem:
    object_name: str
    role: str
    role_group: str
    status: str = "registered"
```

## Acceptance Criteria

- internal part registry survives session round-trips
- it can be read/written together with the existing guided flow state

## Planned Unit Test Scenarios

- default session state carries an empty or absent part registry
- writing the registry and re-reading session state preserves role and
  role-group data
- clearing guided goal state also clears the internal part registry

## Planned E2E / Transport Scenarios

- not required at this micro-leaf; covered by role-registration and transport
  status tests above

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
