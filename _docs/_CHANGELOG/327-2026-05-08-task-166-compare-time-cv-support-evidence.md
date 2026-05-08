# 327. TASK-166 compare-time CV support evidence

Date: 2026-05-08

## Summary

- added packet-local `support_evidence` on
  `server/adapters/mcp/contracts/reference.py` so staged compare packets can
  carry compact deterministic CV summaries without creating a second full
  perception contract
- extended `server/adapters/mcp/areas/reference_silhouette.py` with one
  compare-time support-evidence projection helper that summarizes:
  - prioritized silhouette metrics
  - bounded action-hint summaries
- moved silhouette/action-hint preflight earlier in
  `server/adapters/mcp/areas/reference.py` so packet extraction/ranking requests
  now receive `support_evidence_summaries` before the LLM compare phase runs
- extended packet compare payload text in
  `server/adapters/mcp/vision/prompting.py` so the packet LLM can consume that
  support layer as advisory pre-chewed CV evidence
- added focused coverage for:
  - support-evidence projection on the silhouette owner seam
  - staged compare request threading of support evidence
  - contract-parity support-evidence shape

## Validation

- `git diff --check`
- `poetry run mypy server/adapters/mcp/contracts/reference.py server/adapters/mcp/areas/reference_silhouette.py server/adapters/mcp/areas/reference.py server/adapters/mcp/vision/prompting.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
