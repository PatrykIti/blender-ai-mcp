# TASK-166-02-02: Visual Extraction And Correction Ranking Split

**Parent:** [TASK-166-02](./TASK-166-02_Truth_First_Two_Pass_Compare_Execution.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Separate packet-level visual extraction from later correction ranking so one failed ranking step does not invalidate usable extraction evidence.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`

## Implementation Notes

- Extraction pass should be small and retryable.
- Ranking pass should be skipped when extraction shows a clean packet or too
  little information.

## Acceptance Criteria

- extraction-only success is representable in the compare contract
- ranking is a second bounded phase, not an always-on payload burden
