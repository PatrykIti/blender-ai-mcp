# TASK-130-03: Regression And Docs Closeout For Generic Guided Governor

**Parent:** [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md)
**Depends On:** [TASK-130-01](./TASK-130-01_Default_Guided_Bootstrap_And_Request_Triage_Consistency.md), [TASK-130-02](./TASK-130-02_Generic_Guided_Governor_Hardening_For_Step_Target_And_Domain_Discipline.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Lock the generic guided governor posture in with unit/transport regressions,
operator/prompt docs, and historical closeout.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
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

- unit and transport regressions prove the generic guided governor is more
  disciplined and less drift-prone
- docs explain the generic-first governor story clearly
- board/changelog/docs are updated in the same branch when TASK-130 ships

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-130-03-01](./TASK-130-03-01_Unit_And_Transport_Regression_Matrix_For_Generic_Guided_Governor.md) | Add the regression matrix covering bootstrap/step/target/domain/discovery discipline |
| 2 | [TASK-130-03-02](./TASK-130-03-02_Prompt_Operator_And_Historical_Closeout_For_Generic_Guided_Governor.md) | Align prompts, operator docs, changelog, and board state with the shipped governor behavior |

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

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when TASK-130 ships

## Completion Summary

- added regression coverage for explicit guided-scope requirements, delayed
  inspect escalation, compact/exact-match search, and transport-backed parity
- updated docs, changelog, and board state in the same branch
