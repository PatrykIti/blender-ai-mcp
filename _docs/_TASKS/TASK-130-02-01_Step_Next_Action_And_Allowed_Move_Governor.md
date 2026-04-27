# TASK-130-02-01: Step Next Action And Allowed Move Governor

**Parent:** [TASK-130-02](./TASK-130-02_Generic_Guided_Governor_Hardening_For_Step_Target_And_Domain_Discipline.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Tighten the server-owned step governor so `current_step`, `next_actions`,
`allowed_families`, `allowed_roles`, and related runtime state make the right
next move materially easier than the wrong one.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`

## Detailed Implementation Notes

- reuse the existing guided flow state instead of introducing a second planner
- strengthen step/next-action semantics generically for all domains
- avoid hidden free-run zones where the model can keep calling in-family tools
  without meaningful governor consequences

## Pseudocode Sketch

```python
if current_step == "create_primary_masses" and missing_roles:
    next_actions = ["complete_primary_role_group"]
    allowed_families = ["primary_masses", "reference_context"]
    blocked_families = ["secondary_parts", "finish", "inspect_validate"]
```

## Planned Unit Test Scenarios

- wrong in-family but step-inappropriate moves are bounded more tightly
- `next_actions` stays machine-readable and domain-generic
- role/family/step summaries remain coherent after every transition

## Changelog Impact

- include in the parent TASK-130 changelog entry

## Completion Summary

- stage iterate can now stay in bounded build continuation when the current
  role/workset slice is incomplete, instead of escalating too early
