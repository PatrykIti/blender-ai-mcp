# TASK-150-03-03-02-02: Public Flow Summary And Required Role Groups

**Parent:** [TASK-150-03-03-02](./TASK-150-03-03-02_Guided_Part_Role_Registry_And_Session_Contracts.md)
**Depends On:** [TASK-150-03-03-02-01](./TASK-150-03-03-02-01_Internal_Part_Registry_Session_Key_And_Model.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Expose a compact family/role summary on `guided_flow_state` instead of leaking
the full internal registry into public MCP payloads.

## Repository Touchpoints

- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/router.py`

## Current Code Anchors

- `guided_flow.py` lines 36-48
- `session_capabilities.py` lines 252-314
- `areas/router.py` lines 372-440

## Planned Code Shape

```python
GuidedFlowStateContract(
    ...,
    allowed_roles=["body_core", "head_mass"],
    completed_roles=["body_core"],
    missing_roles=["head_mass"],
    required_role_groups=["primary_masses"],
)
```

## Acceptance Criteria

- public `guided_flow_state` stays compact and machine-readable
- role-group summaries are visible on goal/status payloads

## Planned Unit Test Scenarios

- goal/status contracts serialize `allowed_roles`, `completed_roles`,
  `missing_roles`, and `required_role_groups`
- optional summary fields omit cleanly when no role registry is active

## Planned E2E / Transport Scenarios

- guided status payload over stdio exposes missing role groups after partial
  role registration

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
