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

- Likely implementation shape:
  - one deterministic `build_view_packets(...)` helper under the compare-plan
    owner seam
  - stable packet ids derived from view intent plus selected reference/capture
    slice
- Each packet should name:
  - its target view
  - the reference ids included
  - the capture labels included
  - the compare question for that packet
- View packets should work even when some views are missing.
- Missing or low-quality side/top coverage should degrade to fewer packets or a
  typed blocked/low-information packet outcome rather than collapsing the whole
  compare run.

## Acceptance Criteria

- front-only and front+side runs produce explicit view packets
- missing side/top views degrade to fewer packets instead of one failed monolith
- view packets carry stable packet ids plus packet-local reference/capture
  selection that can be retried independently

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- view-packet unit coverage for missing-view degradation and stable packet ids

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when view-first packet
  planning ships

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when view-first planning closes
  or is split further
