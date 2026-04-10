# TASK-154-03: Regression And Docs Closeout For Guided Naming Policy

**Parent:** [TASK-154](./TASK-154_Guided_Naming_Policy_And_Semantic_Object_Name_Enforcement.md)
**Depends On:** [TASK-154-01](./TASK-154-01_Naming_Policy_Contract_And_Role_Based_Suggestion_Vocabulary.md), [TASK-154-02](./TASK-154-02_Runtime_Advisory_And_Enforcement_Integration_For_Guided_Naming.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Lock the guided naming-policy architecture in with unit/E2E regressions,
prompt/operator docs, and changelog closeout.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- regressions prove warning/block behavior and transport parity
- docs explain both preferred naming and runtime policy behavior
- board/changelog/docs are updated in the same branch when TASK-154 ships

## Detailed Implementation Notes

- this subtask should not invent new runtime semantics
- its job is to prove and document the behavior from `TASK-154-02`
- the closeout should explicitly cover:
  - pure policy evaluation
  - direct guided registration/build integration
  - proxied search/call parity
  - heuristic backstop non-regression
  - prompt/operator docs parity

## Planned Validation Matrix

- unit / pure policy:
  - allowed, warning, blocked, and fallback cases
- unit / runtime integration:
  - `guided_register_part(...)`
  - `guided_role=...`
  - router blocked payloads
  - search/call proxy behavior
- unit / heuristic backstop:
  - relation graph and reference-stage seam recovery still hold
- E2E / stdio:
  - naming warning path
  - naming blocked path
  - session state remains coherent after warnings
- E2E / streamable:
  - same behavior survives transport/session sync
- docs/history:
  - prompt and MCP docs describe the same runtime policy
  - changelog and board state ship together

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-154-03-01](./TASK-154-03-01_Unit_And_Transport_Regression_Matrix_For_Guided_Naming_Policy.md) | Add unit and transport-backed regressions for advisory/block behavior and naming-policy parity |
| 2 | [TASK-154-03-02](./TASK-154-03-02_Prompt_Operator_And_Historical_Closeout_For_Guided_Naming.md) | Align prompts, operator docs, changelog, and board state with the shipped naming policy |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

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

- add a dedicated `_docs/_CHANGELOG/*` entry when TASK-154 ships

## Completion Summary

- completed unit/runtime/docs parity for naming policy
- verified transport-backed parity on the guided stdio/streamable slice
- updated prompts, MCP docs, board state, and changelog in the same branch
