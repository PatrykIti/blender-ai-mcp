# TASK-166-04-01: Simple Model Compare Policy

**Parent:** [TASK-166-04](./TASK-166-04_Complexity_Tiers_And_Multi_Reference_Scaling_Policy.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the minimal compare strategy for simple models so easy cases do not pay the overhead of a super-complex packet pipeline.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference_planner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- one or two reference images can stay on a lightweight packet plan
- simple models do not require unnecessary synthesis stages
