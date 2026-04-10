# TASK-130-02-03: Domain Adaptive Progression And Inspect Escalation

**Parent:** [TASK-130-02](./TASK-130-02_Generic_Guided_Governor_Hardening_For_Step_Target_And_Domain_Discipline.md)
**Depends On:** [TASK-130-02-02](./TASK-130-02-02_Target_Scope_And_Active_Workset_Discipline.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Refine progression and inspect/iterate escalation so the governor remains
generic-first while still adapting correctly to `creature`, `building`, and
fallback `generic` sessions.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/router_helper.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Detailed Implementation Notes

- do not hardcode squirrel-specific progression logic
- prefer:
  - one generic step skeleton
  - domain overlays
  - bounded inspect escalation rules
- inspect/iterate should not strand the model in a dead-end validate state
  when the real next move should still be a bounded build/repair continuation

## Planned Unit Test Scenarios

- `creature` remains anatomy-aware without species-specific hardcoding
- `building` keeps bounded primary/secondary/inspect transitions
- `generic` still behaves sensibly for chair/object/blockout goals

## Changelog Impact

- include in the parent TASK-130 changelog entry
