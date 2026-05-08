# 325. TASK-166 packet guidance contract

Date: 2026-05-08

## Summary

- added `VisionPacketStatusContract` in
  `server/adapters/mcp/sampling/result_types.py` and exposed it through the
  optional `VisionAssistContract.packet_guidance` field
- introduced a packet-specific bounded vision contract in
  `server/adapters/mcp/vision/prompting.py` for staged compare packet runs:
  - request `mode=reference_compare_packet`
  - packet-local payload text with packet id / label / scope / capture slice
  - strict schema with `packet_guidance.packet_status`,
    `packet_guidance.status_reason`, and
    `packet_guidance.ranking_recommendation`
- extended `server/adapters/mcp/vision/parsing.py` so packet compare responses
  normalize or derive packet guidance even when the backend omits the nested
  object
- updated `server/adapters/mcp/areas/reference.py` so staged compare maps the
  parsed packet guidance into `compare_diagnostics` packet extraction/ranking
  status instead of relying only on generic mismatch presence
- added focused coverage for prompt/schema, parser normalization, result-type
  wrapping, and staged compare packet guidance projection

## Runtime / Contract Notes

- This slice does not add a new public MCP tool. It tightens the internal
  packet compare contract used by the existing staged compare / iterate family.
- `VisionAssistContract.packet_guidance` is optional and packet-mode specific.
  Generic compare, checkpoint, and RU flows do not need to populate it.
- Packet guidance remains advisory to the staged compare assembler; deterministic
  truth, gate, and planner ownership stay unchanged.

## Validation

- `git diff --check`
- `poetry run mypy server/adapters/mcp/sampling/result_types.py server/adapters/mcp/vision/prompting.py server/adapters/mcp/vision/parsing.py server/adapters/mcp/areas/reference.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_reference_images.py -q`
