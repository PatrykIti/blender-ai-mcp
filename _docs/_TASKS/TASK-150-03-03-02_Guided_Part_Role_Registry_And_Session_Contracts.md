# TASK-150-03-03-02: Guided Part Role Registry And Session Contracts

**Parent:** [TASK-150-03-03](./TASK-150-03-03_Generic_Families_Part_Roles_And_Execution_Enforcement.md)
**Depends On:** [TASK-150-03-03-01](./TASK-150-03-03-01_Shared_Tool_Family_Vocabulary_And_Overlay_Mapping.md)
**Status:** 🚧 In Progress
**Priority:** 🔴 High

## Objective

Add a session-scoped part-role registry so the server can tell whether an
existing or newly created object is acting as a primary mass, appendage pair,
roof mass, facade opening, and so on.

## Repository Touchpoints

- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/contracts/router.py`

## Acceptance Criteria

- session state can persist a bounded part-role registry
- `guided_flow_state` can expose a compact machine-readable summary of:
  - allowed roles
  - completed roles
  - missing roles
  - required role groups
- the contract remains small enough for public MCP payloads

## Detailed Implementation Notes

- keep the full registry internal/session-scoped if needed
- only expose compact summaries on the public `guided_flow_state` surface
- likely internal fields per registered part:
  - `object_name`
  - `role`
  - `role_group`
  - `status`
  - `created_in_step`
- likely public summaries on `guided_flow_state`:
  - `allowed_families`
  - `allowed_roles`
  - `completed_roles`
  - `missing_roles`
  - `required_role_groups`

## Current Code Anchors

- `server/adapters/mcp/session_capabilities.py`
  - lines 29-44: current session keys
  - lines 95-122: current `SessionCapabilityState`
  - lines 317-339: current state loading
  - lines 388-411: current state persistence
- `server/adapters/mcp/contracts/guided_flow.py`
  - lines 36-48: current public flow contract
- `server/adapters/mcp/areas/router.py`
  - lines 372-440: current public exposure on goal/status payloads

## Pseudocode Sketch

```python
SESSION_GUIDED_PART_REGISTRY_KEY = "guided_part_registry"

class GuidedPartRegistryItemContract(MCPContract):
    object_name: str
    role: str
    role_group: str
    status: Literal["planned", "registered", "validated"]
    created_in_step: GuidedFlowStepLiteral | None = None

class GuidedFlowStateContract(MCPContract):
    ...
    allowed_families: list[str] = []
    allowed_roles: list[str] = []
    completed_roles: list[str] = []
    missing_roles: list[str] = []
    required_role_groups: list[str] = []
```

## Planned Unit Test Scenarios

- session state round-trips the internal part registry
- `guided_flow_state` exposes compact role summaries only
- overlay initialization sets the correct initial `allowed_roles` and
  `required_role_groups`

## Planned E2E / Transport Scenarios

- stdio guided creature session:
  - register `body_core` / `head_mass`
  - `router_get_status()` reflects completed and missing roles
- streamable guided building session:
  - register `main_volume`
  - verify the same role summary survives in the same MCP session

## Execution Structure

| Order | Micro-Leaf | Purpose |
|------|------------|---------|
| 1 | [TASK-150-03-03-02-01](./TASK-150-03-03-02-01_Internal_Part_Registry_Session_Key_And_Model.md) | Add the internal session-scoped part registry and persistence hooks |
| 2 | [TASK-150-03-03-02-02](./TASK-150-03-03-02-02_Public_Flow_Summary_And_Required_Role_Groups.md) | Expose compact role/family summaries on `guided_flow_state` instead of leaking the full registry |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Changelog Impact

- include in the parent TASK-150 execution-enforcement changelog entry
