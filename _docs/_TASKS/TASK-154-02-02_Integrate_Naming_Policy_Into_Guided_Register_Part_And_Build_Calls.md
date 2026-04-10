# TASK-154-02-02: Integrate Naming Policy Into Guided Register Part And Build Calls

**Parent:** [TASK-154-02](./TASK-154-02_Runtime_Advisory_And_Enforcement_Integration_For_Guided_Naming.md)
**Depends On:** [TASK-154-02-01](./TASK-154-02-01_Shared_Guided_Naming_Policy_Module_And_Opaque_Name_Detection.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Run the shared naming policy on the canonical guided registration path and on
role-sensitive build calls that carry `guided_role=...`.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Detailed Implementation Notes

- `guided_register_part(...)` remains the canonical explicit path
- `guided_role=...` remains convenience-only, but should use the same naming
  decision logic
- do not fork separate role-to-name logic into router and modeling adapters

## Planned File Change Map

- `server/adapters/mcp/areas/router.py`
  - run policy before guided registration is committed
- `server/adapters/mcp/areas/modeling.py`
  - run policy on role-sensitive create/transform success paths
- `server/adapters/mcp/router_helper.py`
  - preserve coherent blocked payload semantics
- `server/adapters/mcp/guided_naming_policy.py`
  - provide one reusable integration call
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - verify registration/build path behavior with session state
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
  - verify domain-specific suggestion differences
- `tests/unit/adapters/mcp/test_router_elicitation.py`
  - verify user/model-facing blocked payloads
- `tests/unit/adapters/mcp/test_search_surface.py`
  - verify proxied calls preserve the same behavior
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - verify stdio same-session parity
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - verify streamable same-session parity

## Pseudocode Sketch

```python
decision = evaluate_guided_object_name(
    object_name=object_name,
    role=role,
    domain_profile=current_flow.domain_profile,
    current_step=current_flow.current_step,
)

if decision.status == "blocked":
    return blocked_payload_with_guidance(decision)

result = register_or_build(...)
return attach_naming_guidance_if_needed(result, decision)
```

## Acceptance Criteria

- both canonical registration and convenience build-role paths use one policy
- warning/block behavior is consistent across those paths

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-154 changelog entry
