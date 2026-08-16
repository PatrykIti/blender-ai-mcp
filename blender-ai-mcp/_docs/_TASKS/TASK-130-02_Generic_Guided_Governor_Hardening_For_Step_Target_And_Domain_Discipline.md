# TASK-130-02: Generic Guided Governor Hardening For Step Target And Domain Discipline

**Parent:** [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md)
**Depends On:** [TASK-130-01](./TASK-130-01_Default_Guided_Bootstrap_And_Request_Triage_Consistency.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Use and extend the existing server-driven guided runtime so the governor keeps
the model on the right step, target/workset, and domain-adaptive progression
path without squirrel-specific hacks.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Acceptance Criteria

- the governor more reliably constrains the model to valid next moves using
  existing server-owned flow/visibility/role/target state
- target/workset behavior is more reliable and generic across:
  - `creature`
  - `building`
  - `generic`
- inspect/iterate escalation becomes more bounded and less likely to strand the
  model in a dead-end validate state
- search/discovery becomes tighter for the current step/domain/workset

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-130-02-01](./TASK-130-02-01_Step_Next_Action_And_Allowed_Move_Governor.md) | Tighten the step/next-action governor so the current runtime state drives the next bounded move more strongly |
| 2 | [TASK-130-02-02](./TASK-130-02-02_Target_Scope_And_Active_Workset_Discipline.md) | Strengthen target/workset discipline so the model operates on the right objects/collections at the right time |
| 3 | [TASK-130-02-03](./TASK-130-02-03_Domain_Adaptive_Progression_And_Inspect_Escalation.md) | Refine generic/domain-adaptive progression and inspect escalation rules without adding squirrel-only branches |
| 4 | [TASK-130-02-04](./TASK-130-02-04_Search_And_Discovery_Shaping_For_Current_Governor_State.md) | Shape search/discovery around the current governor state so results stay bounded and useful |

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-130 changelog entry

## Completion Summary

- reused the existing guided runtime pieces instead of adding a second planner
- tightened step/target/discovery behavior generically across the guided loop
