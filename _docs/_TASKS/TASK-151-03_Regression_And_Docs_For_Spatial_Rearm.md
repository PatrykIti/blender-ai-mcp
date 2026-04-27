# TASK-151-03: Regression And Docs For Spatial Re-Arm

**Parent:** [TASK-151](./TASK-151_Spatial_Check_Freshness_Target_Binding_And_Guided_Rearm.md)
**Depends On:** [TASK-151-01](./TASK-151-01_Target_Bound_Spatial_Check_Validity.md), [TASK-151-02](./TASK-151-02_Spatial_Freshness_And_Rearm_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Protect the target-bound/freshness-aware spatial model with regression tests
and operator docs.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Acceptance Criteria

- tests prove that spatial checks cannot be spoofed by unrelated objects
- tests prove that spatial checks can be re-armed after material scene changes
- docs explain when the model must refresh spatial context instead of pushing
  forward with stale facts

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-151-03-01](./TASK-151-03-01_Unit_And_Transport_Regression_Matrix_For_Spatial_Freshness.md) | Add unit and transport-backed regression coverage for target-bound and stale-spatial behavior |
| 2 | [TASK-151-03-02](./TASK-151-03-02_Public_Docs_And_Troubleshooting_For_Spatial_Rearm.md) | Align README/MCP/prompt docs with the new target-bound freshness model |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-151 changelog entry

## Detailed Implementation Notes

- docs must describe only the shipped runtime contract:
  - active target scope
  - target-bound validity
  - spatial freshness/version fields
  - `spatial_refresh_required`
  - `next_actions=["refresh_spatial_context"]`
- parity tests should assert the same public story across:
  - README
  - MCP server docs
  - prompt/operator docs
  - transport payloads

## Status / Closeout Note

- closed on 2026-04-09 together with the runtime implementation so regression
  coverage and public docs match the final shipped behavior

## Completion Summary

- added target-bound/freshness-aware regression coverage across unit and
  transport layers
- updated README, MCP docs, prompt docs, changelog, and task board for the new
  guided spatial re-arm contract
