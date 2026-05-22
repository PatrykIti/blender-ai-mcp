# 363. TASK-172 localization runtime and transport

Date: 2026-05-23

## Summary

Landed the `TASK-172-03` localization slice and closed the current
`TASK-172-05` lifecycle verdict from evidence, while keeping the umbrella open
for the remaining harness and final closeout work.

## Changes

- added one default-off compare-time localization config surface on the shared
  vision runtime:
  - `VISION_LOCALIZATION_ENABLED`
  - `VISION_LOCALIZATION_PROVIDER`
  - `VISION_LOCALIZATION_ENDPOINT`
  - `VISION_LOCALIZATION_MODEL`
  - `VISION_LOCALIZATION_API_KEY` / `VISION_LOCALIZATION_API_KEY_ENV`
  - `VISION_LOCALIZATION_TIMEOUT_SECONDS`
  - `VISION_LOCALIZATION_MAX_CANDIDATES`
- added one provider-neutral internal `VisionLocalizationCandidate` contract
  with packet/reference/view provenance plus literal `box_xyxy`
- implemented compare-time localization collection on the packet owner seam and
  kept localization boxes internal
- projected localization-only support-safe `crop_path` plus derived
  `box_center` anchors through the existing `part_segmentation` carrier
- allowed localization candidates to seed compare-time segmentation through
  internal `seed_boxes`
- generalized compare-time support summaries to say `Optional localized
  support...`, so the same packet carrier can represent both localization and
  segmentation-sidecar support cleanly
- extended transport proof to cover localization sidecar compare packets on
  stdio and streamable HTTP
- updated `TASK-172-03`, `TASK-172-03-01`, and `TASK-172-03-02` to `✅ Done`
  with explicit completion summaries
- closed `TASK-172-05` with the explicit `request_scoped_only` verdict because
  the current family still ships only sidecar/external optional support, not a
  reusable in-process heavy-local adapter owner
- updated `_docs/_VISION/*`, `_docs/_MCP_SERVER/*`, `.env.example`, and the
  `TASK-172` umbrella/board notes to describe the shipped localization seam

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q -k 'localization_sidecar_transport'`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Notes

- `TASK-172` is still not complete
- the remaining open work is the localized-support harness/negative-coverage
  lane (`TASK-172-06`) plus final board/changelog closeout (`TASK-172-07`)
