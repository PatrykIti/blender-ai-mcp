# TASK-166-04-02: Complex And Super-Complex Compare Policy

**Parent:** [TASK-166-04](./TASK-166-04_Complexity_Tiers_And_Multi_Reference_Scaling_Policy.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the packet scheduler and synthesis posture for complex and super-complex 6-12 image compare runs.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/e2e/vision/`

## Implementation Notes

- Large runs should default to:
  - one image or a small paired packet at a time
  - packet synthesis afterward
  - conflict/uncertainty reporting across packets

## Acceptance Criteria

- 6-12 image runs stay bounded and explain packet conflicts explicitly
- synthesis remains short enough for generic LLM operators
- packet conflict/uncertainty reporting can feed both additive staged compare
  diagnostics and the compact `reference_orchestrator_feedback` summary
