# TASK-166-01-01: View-First Packet Planner

**Parent:** [TASK-166-01](./TASK-166-01_View_And_Scope_Packet_Compare_Family.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Plan compare packets by view (`front`, `side`, optional `top` / silhouette) so each packet can be retried and interpreted independently.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/capture.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- Each packet should name:
  - its target view
  - the reference ids included
  - the capture labels included
  - the compare question for that packet
- View packets should work even when some views are missing.

## Acceptance Criteria

- front-only and front+side runs produce explicit view packets
- missing side/top views degrade to fewer packets instead of one failed monolith
- view packets carry stable packet ids plus packet-local reference/capture
  selection that can be retried independently
