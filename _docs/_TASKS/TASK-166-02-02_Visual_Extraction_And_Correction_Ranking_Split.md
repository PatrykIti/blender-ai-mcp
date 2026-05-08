# TASK-166-02-02: Visual Extraction And Correction Ranking Split

**Parent:** [TASK-166-02](./TASK-166-02_Truth_First_Two_Pass_Compare_Execution.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Separate packet-level visual extraction from later correction ranking so one failed ranking step does not invalidate usable extraction evidence.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Implementation Notes

- Extraction pass should be small and retryable.
- Ranking pass should be skipped when extraction shows a clean packet or too
  little information.
- Both phases still project back through the staged compare assembler; this leaf
  does not create a second iterate-owned ranking path.
- Packet status, skip reasons, and ranking failure details should stay explicit
  enough for additive compare diagnostics and compact orchestrator projection.

## Acceptance Criteria

- extraction-only success is representable in the compare contract
- ranking is a second bounded phase, not an always-on payload burden
- extraction and ranking can expose independent packet status so a clean,
  low-information, skipped, or failed ranking phase is explicit instead of
  being inferred from omission
- ranking skipped after a clean or low-information extraction is represented as
  an intentional outcome with a reason, not as a hidden failure

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- staged compare/iterate contract tests covering extraction-only success,
  ranking skip, and ranking failure projection
- `tests/e2e/integration/test_guided_gate_state_transport.py` when packet
  status or diagnostics become client-visible

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when extraction/ranking
  split semantics ship

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
