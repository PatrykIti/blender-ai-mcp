# 328. TASK-166 packet policy repair and proof

Date: 2026-05-08

## Summary

- moved durable TASK-166 packet-planning / packet-synthesis policy into the
  staged-compare helper seam now located at
  `server/adapters/mcp/areas/reference_compare_packets.py` so view/scope
  decomposition, phase-result merging, diagnostics emission, and synthesized
  input-summary policy are no longer concentrated only inside
  `server/adapters/mcp/areas/reference.py`
- repaired simple-tier view-first behavior:
  - front + side staged captures now emit explicit per-view packets
  - reference-only views no longer create mixed front+side packets when the
    current staged capture set never captured that view
  - clean compact single-packet runs can omit additive `compare_diagnostics`
    again, while ranking/extraction uncertainty still forces diagnostics back on
    the public staged surface
- repaired complex-tier scope behavior:
  - focus-pair planning now preserves packet-local `target_view` on complex
    packets instead of dropping secondary views
  - common creature seams now group into semantic scope labels such as
    `Body + Head`, `Tail`, and `Ears`
- made compare-time `support_evidence` packet-local and typed:
  - packet diagnostics now carry compact machine-readable support-evidence items
    instead of only free-form strings
  - packet-local capture/reference provenance is preserved on each item
  - prompt/runtime payloads still receive bounded string summaries derived from
    that typed evidence
- tightened packet-state handling:
  - staged compare packets now project explicit `packet_status` and
    `ranking_recommendation`
  - successful ranking can replace extraction guidance when the second pass
    returns narrower packet-local focus
  - packet-guidance fallback parsing now requires an actual clean signal before
    skipping ranking
- corrected synthesized packet input summaries so reused captures/references are
  deduped instead of being summed repeatedly across packets
- expanded proof lanes:
  - added focused planner coverage in
    `tests/unit/adapters/mcp/test_reference_compare_packets.py`
  - added compact/rich regression coverage in
    `tests/unit/adapters/mcp/test_reference_images.py`
  - extended transport and Blender-backed E2E assertions for
    `compare_diagnostics`, packet status, and packet-local support evidence

## Validation

- `git diff --check`
- `poetry run mypy server/adapters/mcp/areas/reference_compare_packets.py server/adapters/mcp/contracts/reference.py server/adapters/mcp/areas/reference_silhouette.py server/adapters/mcp/areas/reference_planner.py server/adapters/mcp/areas/reference.py server/adapters/mcp/vision/parsing.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
