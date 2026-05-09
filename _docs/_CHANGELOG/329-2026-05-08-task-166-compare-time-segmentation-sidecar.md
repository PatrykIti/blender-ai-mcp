# 329. TASK-166 compare-time segmentation sidecar

Date: 2026-05-08

## Summary

- extended staged `reference_compare_stage_checkpoint(...)` /
  `reference_iterate_stage_checkpoint(...)` packet execution so the optional
  segmentation sidecar can now run as bounded advisory-only compare support
  instead of surfacing only a disabled/unavailable placeholder
- added one staged-compare-owned segmentation collection/merge path under
  `server/adapters/mcp/areas/reference_compare_packets.py` that:
  - accepts packet-local references and captures
  - normalizes sidecar `parts` payloads into the existing
    `ReferencePartSegmentationContract`
  - degrades failures to bounded availability notes without breaking the staged
    loop
- extended packet-local `support_evidence` to include
  `evidence_kind="part_segmentation"` so compare prompts can consume compact
  part-aware sidecar cues on the same additive staged contract
- updated staged compare docs/task state to reflect that compare-time optional
  segmentation support is now live while remaining default-off and
  advisory-only

## Runtime / Contract Notes

- `part_segmentation` remains additive on staged compare/iterate responses and
  stays `status="disabled"` unless the optional segmentation sidecar is
  explicitly enabled on runtime config.
- When enabled, the sidecar runs per bounded compare packet and merges its
  returned parts into the top-level `part_segmentation` payload plus packet
  `support_evidence`.
- Sidecar output is still non-authoritative: failures or empty payloads degrade
  to `status="unavailable"` notes and do not become the sole basis for packet
  completion or correction ranking.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
