# TASK-150-03-03-06: Regression And Docs For Execution Enforcement

**Parent:** [TASK-150-03-03](./TASK-150-03-03_Generic_Families_Part_Roles_And_Execution_Enforcement.md)
**Depends On:** [TASK-150-03-03-04](./TASK-150-03-03-04_Router_Execution_Guards_And_Blocked_Response_Policy.md), [TASK-150-03-03-05](./TASK-150-03-03-05_Flow_Transitions_From_Role_Groups_And_Checkpoints.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Protect the execution-enforcement continuation of TASK-150 with unit/E2E
coverage and explicit operator docs so the server-owned sequencing contract is
auditable in real sessions.

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`
- `tests/e2e/router/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `README.md`

## Acceptance Criteria

- tests prove that the server can block the wrong family/role even when the
  model tries to call visible/internal-looking tools directly
- tests prove that completing the right role groups unlocks the next family
- docs explain:
  - what families are
  - what part roles are
  - why this does not require a separate macro tool per domain part

## Detailed Implementation Notes

- the regression matrix should explicitly include:
  - one creature primary-mass block case
  - one creature secondary-part early block case
  - one building overlay case
  - one search/list/call parity case after role registration
- operator docs should explain that:
  - prompt bundles support the flow
  - the server/runtime remains the authority for family/role enforcement

## Current Code Anchors

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Pseudocode Sketch

```python
def test_creature_secondary_parts_blocked_before_primary_role_groups_complete():
    ...
    blocked = call_tool("modeling_create_primitive", {"guided_role": "ear_pair", ...})
    assert blocked["guided_flow_state"]["current_step"] == "create_primary_masses"
    assert "allowed_roles" in blocked["error"] or blocked["guided_flow_state"]["missing_roles"]
```

## Planned Unit Test Scenarios

- prove block-on-wrong-family
- prove block-on-wrong-role
- prove unlock-after-role-registration
- prove step transition after required role groups

## Planned E2E / Transport Scenarios

- stdio same-session creature flow from goal -> spatial checks -> primary
  masses -> secondary parts -> checkpoint iterate
- streamable same-session parity for the same family/role unlock path
- router manual-handoff path proves the server still enforces execution order
  after `no_match`

## Execution Structure

| Order | Micro-Leaf | Purpose |
|------|------------|---------|
| 1 | [TASK-150-03-03-06-01](./TASK-150-03-03-06-01_Unit_And_Transport_Regression_Matrix_For_Family_Role_Enforcement.md) | Add unit and transport-backed regressions for family/role blocking and unlock transitions |
| 2 | [TASK-150-03-03-06-02](./TASK-150-03-03-06-02_Operator_Docs_And_Troubleshooting_For_Execution_Enforcement.md) | Explain execution-enforcement semantics and troubleshooting in public docs |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/e2e/integration/test_guided_flow_step_gating.py`
- `tests/e2e/router/test_guided_flow_step_gating_router_paths.py`

## Changelog Impact

- include in the parent TASK-150 execution-enforcement changelog entry

## Completion Summary

- added unit and transport-backed regression coverage for the current
  family/role execution-enforcement slice
- aligned README/MCP/prompt docs with the new runtime contract
- the remaining follow-on work for TASK-150 now sits outside the original
  execution-enforcement planning slice rather than inside this regression/doc
  wave
