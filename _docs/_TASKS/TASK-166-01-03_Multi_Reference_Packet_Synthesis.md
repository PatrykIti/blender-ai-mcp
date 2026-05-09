# TASK-166-01-03: Multi-Reference Packet Synthesis

**Parent:** [TASK-166-01](./TASK-166-01_View_And_Scope_Packet_Compare_Family.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Merge packet-level compare results into one short synthesis summary that generic LLM operators can read without replaying every packet transcript.

## Completion Summary

- packeted staged compare now synthesizes successful packet outputs back into
  one compact `VisionAssistContract` result instead of forcing callers to
  inspect each packet separately
- additive `compare_diagnostics` now surface packet order, synthesis
  requirement/status, packet-local evidence summaries, and uncertainty notes on
  the existing staged compare / iterate contracts
- compact `reference_orchestrator_feedback` now projects synthesized packet
  rationale and uncertainty without exposing raw packet internals as the main
  orchestration seam

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/application/services/reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Implementation Notes

- Synthesis should preserve provenance back to packet ids/reference ids.
- Contradictory packet conclusions must surface uncertainty, not be silently
  collapsed.
- Likely implementation shape:
  - one packet-synthesis helper under `reference_planner.py`
  - one compact feedback projection path that can summarize conflicts without
    forcing raw packet replay
- If additive `compare_diagnostics` ships, synthesis should wire packet
  provenance/conflicts there and project a compact uncertainty summary through
  `reference_orchestrator_feedback` rather than forcing orchestration clients to
  parse raw packet payloads.

## Acceptance Criteria

- packet results can be merged into one compact summary
- provenance and uncertainty survive synthesis
- packet conflicts surface explicitly instead of being silently merged into one
  optimistic correction list

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- packet-synthesis unit coverage for provenance retention and conflict
  projection
- `tests/e2e/integration/test_guided_gate_state_transport.py` when synthesis
  changes client-visible staged compare / iterate payloads

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when packet synthesis ships

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when synthesis/provenance work
  closes or is split further

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
