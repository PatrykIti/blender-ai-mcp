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

- Likely implementation shape:
  - one packet-preflight helper that resolves deterministic inputs first
  - one packet-question builder that receives the resolved truth slice plus
    selected captures/reference ids
- Preflight must always be grounded in:
  - `scene_scope_graph`
  - `scene_relation_graph`
  - `scene_view_diagnostics`
- Packet questions should be narrow, for example:
  - "Is tail silhouette too short from side?"
  - "Are ears visible and readable from front?"
- Error cases to make explicit:
  - missing reference slice
  - missing target view coverage
  - preflight ambiguity that should yield a typed blocked or low-information
    packet instead of a broad fallback prompt

## Acceptance Criteria

- the compare family can express packet-specific questions
- deterministic preflight stays first authority
- packet question contracts can name the packet id, selected reference ids,
  selected capture labels, and required deterministic inputs for that packet

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
