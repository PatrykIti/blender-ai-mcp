# TASK-130-02-02: Target Scope And Active Workset Discipline

**Parent:** [TASK-130-02](./TASK-130-02_Generic_Guided_Governor_Hardening_For_Step_Target_And_Domain_Discipline.md)
**Depends On:** [TASK-130-02-01](./TASK-130-02-01_Step_Next_Action_And_Allowed_Move_Governor.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Strengthen the generic guided governor around target scope and active workset
discipline so the model acts on the right object set or collection at the
right time.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Detailed Implementation Notes

- build on:
  - active target scope
  - scope fingerprinting
  - spatial re-arm/freshness
- extend that discipline into a more explicit workset concept where helpful:
  - current target objects
  - current collection/workset
  - currently allowed object family/role set
- keep this generic:
  - creature = body/head/tail/limbs
  - building = footprint/main volume/openings/supports
  - generic = best-effort anchor/core/secondary object groups

## Planned E2E Scenarios

- creature:
  - unrelated helper target cannot unlock the next bounded move
- building:
  - target collection/workset must stay consistent across primary/secondary steps
- generic:
  - a chair/object-style blockout still gets one bounded active workset even
    without a specialized domain recipe

## Changelog Impact

- include in the parent TASK-130 changelog entry

## Completion Summary

- active guided spatial-gate helpers now require explicit scope consistently
  across `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
  `scene_view_diagnostics(...)`
