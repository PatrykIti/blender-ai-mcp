# TASK-166-01-03: Multi-Reference Packet Synthesis

**Parent:** [TASK-166-01](./TASK-166-01_View_And_Scope_Packet_Compare_Family.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Merge packet-level compare results into one short synthesis summary that generic LLM operators can read without replaying every packet transcript.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/contracts/reference.py`

## Implementation Notes

- Synthesis should preserve provenance back to packet ids/reference ids.
- Contradictory packet conclusions must surface uncertainty, not be silently
  collapsed.

## Acceptance Criteria

- packet results can be merged into one compact summary
- provenance and uncertainty survive synthesis
