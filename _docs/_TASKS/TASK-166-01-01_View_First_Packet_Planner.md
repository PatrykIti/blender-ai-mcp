# TASK-166-01-01: View-First Packet Planner

**Parent:** [TASK-166-01](./TASK-166-01_View_And_Scope_Packet_Compare_Family.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Plan compare packets by view (`front`, `side`, optional `top` / silhouette) so each packet can be retried and interpreted independently.

## Completion Summary

- simple staged compare runs now emit explicit per-view packets for front/side
  evidence instead of collapsing those views into one mixed packet
- packet view selection now follows the deterministic stage capture set first;
  reference-only views no longer create implicit mixed packets when the current
  stage never captured that view
- explicit `target_view` requests can still degrade into typed packet-local
  low-information outcomes when the requested view is missing from the current
  staged capture set

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
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- view-packet unit coverage for missing-view degradation and stable packet ids
- post-closeout audit proof now covers stable packet ids across equivalent
  scheduler inputs and extraction/ranking retry requests

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- view-first packet planning shipped through the TASK-166 packeted compare
  closeout and subsequent hardening changelog entries.

## Status / Board Update

- parent `TASK-166` and this leaf are aligned as `✅ Done`; no open follow-on
  remains for view-first packet planning.
