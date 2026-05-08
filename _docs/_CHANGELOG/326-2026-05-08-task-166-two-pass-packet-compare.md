# 326. TASK-166 two-pass packet compare

Date: 2026-05-08

## Summary

- split staged compare packet execution in
  `server/adapters/mcp/areas/reference.py` into two bounded phases:
  - packet extraction first
  - packet ranking second only when extraction returns
    `ranking_recommendation="rank"`
- extended the packet compare prompt/schema/parser seams so packet requests can
  distinguish:
  - `compare_phase=packet_extraction`
  - `compare_phase=packet_ranking`
- packet ranking requests now receive bounded extraction evidence in metadata so
  the second pass can rank already-extracted mismatches instead of redoing the
  whole packet compare from scratch
- ranking failure now preserves extraction evidence and marks the packet
  `ranking_status="error"` in `compare_diagnostics`
- clean / low-information / blocked packet outcomes now skip the ranking pass
  explicitly and keep that skip reason visible on the staged compare surface
- staged packet diagnostics now also preserve explicit packet
  `packet_status` / `ranking_recommendation`, and compact ranking failures keep
  those diagnostics visible instead of being dropped from the public response
- compact `reference_orchestrator_feedback` now picks up packet uncertainty
  notes from `compare_diagnostics`, including ranking-failure summaries

## Validation

- `git diff --check`
- `poetry run mypy server/adapters/mcp/sampling/result_types.py server/adapters/mcp/vision/prompting.py server/adapters/mcp/vision/parsing.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_feedback.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
