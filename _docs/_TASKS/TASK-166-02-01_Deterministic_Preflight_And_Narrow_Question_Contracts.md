# TASK-166-02-01: Deterministic Preflight And Narrow Question Contracts

**Parent:** [TASK-166-02](./TASK-166-02_Truth_First_Two_Pass_Compare_Execution.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the deterministic preflight and narrow packet question contract that sits in front of any LLM compare call.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/runner.py`

## Implementation Notes

- Preflight must always be grounded in:
  - `scene_scope_graph`
  - `scene_relation_graph`
  - `scene_view_diagnostics`
- Packet questions should be narrow, for example:
  - "Is tail silhouette too short from side?"
  - "Are ears visible and readable from front?"

## Acceptance Criteria

- the compare family can express packet-specific questions
- deterministic preflight stays first authority
