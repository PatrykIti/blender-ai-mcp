# TASK-154-03-01: Unit And Transport Regression Matrix For Guided Naming Policy

**Parent:** [TASK-154-03](./TASK-154-03_Regression_And_Docs_Closeout_For_Guided_Naming_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Build the regression matrix proving guided naming policy works consistently in
unit/runtime and in transport-backed guided sessions.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Planned Unit Test Scenarios

- policy module:
  - semantic name is allowed
  - weak name returns warning with suggestions
  - opaque role-sensitive name blocks in strict mode
- role/domain vocabulary:
  - creature and building roles produce different deterministic suggestions
- guided runtime:
  - `guided_register_part(...)` carries naming guidance
  - `guided_role=...` build path carries the same naming guidance
  - domain-profile overlays still resolve correct role vocabulary
- router/runtime policy:
  - blocked payload includes actionable message and machine-readable reason
- search/proxy parity:
  - `call_tool(...)` preserves warning/block behavior for visible guided tools
- heuristic backstop:
  - relation graph still recognizes abbreviated limb names when advisory mode is
    in use
  - reference-stage truth bundle still recognizes abbreviated limb names when
    advisory mode is in use
- transport:
  - stdio guided session receives deterministic naming warning message
  - stdio guided session receives deterministic naming blocked message
  - streamable guided session receives the same behavior without session drift

## Pseudocode Sketch

```python
blocked = call_tool(
    "modeling_create_primitive",
    {"name": "ForeL", "guided_role": "foreleg_pair", ...},
)
assert "ForeLeg_L" in blocked["message"]
assert blocked["guided_naming"]["status"] in {"warning", "blocked"}
```

## Planned E2E / Transport Scenarios

- stdio:
  - `guided_register_part(object_name="ForeL", role="foreleg_pair")`
    returns warning or block with semantic suggestions
  - `modeling_create_primitive(name="ForeL", guided_role="foreleg_pair", ...)`
    returns the same policy result shape
  - canonical names like `ForeLeg_L` remain allowed
- streamable:
  - same warning/block decisions survive transport state sync
  - search/list/status remain coherent after a naming warning

## Planned File Change Map

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
  - pure policy coverage
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - registration/build integration coverage
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
  - domain-specific suggestion coverage
- `tests/unit/adapters/mcp/test_router_elicitation.py`
  - blocked payload semantics coverage
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
  - docs parity coverage
- `tests/unit/adapters/mcp/test_search_surface.py`
  - proxy/discovery parity coverage
- `tests/unit/adapters/mcp/test_reference_images.py`
  - heuristic backstop coverage on reference-stage truth
- `tests/unit/tools/test_handler_rpc_alignment.py`
  - heuristic backstop coverage on relation graph planning
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - stdio transport coverage
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - streamable transport coverage

## Acceptance Criteria

- regressions prove advisory and blocked behavior across unit and transport

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-154 changelog entry
