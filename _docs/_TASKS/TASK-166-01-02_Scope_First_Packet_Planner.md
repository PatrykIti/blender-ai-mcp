# TASK-166-01-02: Scope-First Packet Planner

**Parent:** [TASK-166-01](./TASK-166-01_View_And_Scope_Packet_Compare_Family.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Plan compare packets by active scope clusters such as `Body + Head`, `Tail`, and `Ears` instead of always comparing the full assembled model.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- Scope packets should align with current guided step, gate blockers, and active
  target scope.
- Scope packets should map back to existing truth pairs/object clusters instead
  of inventing a second scope graph beside the staged compare truth bundle.
- Packet planning must remain generic across domains.

## Acceptance Criteria

- compare packets can isolate one blocker cluster
- large assembled models no longer force every compare to include every part
- scope packets identify the object cluster / truth-pair slice they own so later
  synthesis and feedback can attribute findings without guessing
