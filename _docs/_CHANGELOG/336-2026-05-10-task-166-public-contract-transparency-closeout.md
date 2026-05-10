# 336. TASK-166 public contract transparency closeout

Date: 2026-05-10
Task: `TASK-166-06`

## Summary

- Closed the public transparency lane for the hierarchical staged compare
  family.
- Kept detailed packet provenance on additive top-level `compare_diagnostics`
  while adding bounded
  `correction_candidates[*].vision_evidence.packet_evidence_refs` pointers for
  candidate-level join-back.
- Hardened public tool docstrings, router metadata, user docs, and test docs for
  packet ids, pass status, `support_evidence`, `budget_control`, compact
  iterate debug omission, and compact feedback projection.
- Closed the `TASK-166` umbrella after packet planning, two-pass compare,
  compare-time CV/segmentation support, runtime budget diagnostics,
  super-complex packet scheduling, and public transparency shipped.

## Runtime / Contract Notes

- No public MCP tool names changed.
- `reference_orchestrator_feedback` remains the compact orchestration-facing
  owner seam.
- `compare_diagnostics` remains the full packet provenance owner.
- `correction_candidates` remain compact ranked action items and carry only
  bounded packet refs for provenance.

## Validation

- `poetry run ruff check server/adapters/mcp/contracts/reference.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_planner.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/e2e/integration/test_guided_gate_state_transport.py`
  - passed
- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - passed, `146 passed`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
  - passed, `16 passed`
- `poetry run pytest ./tests/unit`
  - passed, `3311 passed`
- `poetry run pytest tests/e2e/integration/test_mcp_transport_modes.py::test_stdio_transport_e2e_keeps_same_session_id_across_calls_in_one_client -q`
  - passed after isolating the first full-run stdio startup timeout, `1 passed`
- `poetry run python ./scripts/run_e2e_tests.py`
  - passed on rerun, `468 passed, 3 skipped`
