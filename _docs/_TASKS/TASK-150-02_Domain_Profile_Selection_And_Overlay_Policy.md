# TASK-150-02: Domain Profile Selection And Overlay Policy

**Parent:** [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add deterministic domain-profile selection for guided sessions and define how
 domain overlays modify the generic flow.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/router/application/session_phase_hints.py`
- `server/adapters/mcp/prompts/prompt_catalog.py`

## Acceptance Criteria

- the flow system can deterministically choose at least:
  - `generic`
  - `creature`
  - `building`
- profile selection uses goal/handoff/runtime state, not prompt text alone
- the overlay policy defines how each profile can change:
  - steps
  - required checks
  - required prompts
  - allowed tool families

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- prompt/goal-tag tests as needed

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-150-02-01](./TASK-150-02-01_Generic_Flow_Skeleton_And_Step_Vocabulary.md) | Define the generic server-driven flow skeleton and shared step vocabulary |
| 2 | [TASK-150-02-02](./TASK-150-02-02_Creature_And_Building_Domain_Overlay_Policies.md) | Define the first domain overlays for creature and building guided flows |
