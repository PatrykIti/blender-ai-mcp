# 333. TASK-166 backend packet-guidance normalization

Date: 2026-05-10

## Summary

- repaired the real external vision backend path so parsed packet guidance now
  survives backend normalization into `VisionAssistContract`
- kept packet status and ranking normalization owned by
  `server/adapters/mcp/vision/parsing.py`; provider backends now only forward
  the parser-owned `packet_guidance` field
- added a backend-level regression that exercises an OpenAI-compatible
  packet-mode request and validates typed
  `VisionPacketStatusContract.packet_status` plus
  `ranking_recommendation`
- cleaned trailing status-line whitespace in the affected TASK-166 task files
  so closeout validation can rely on `git diff --check`

## Runtime / Contract Notes

- public MCP tool names and staged compare / iterate response fields are
  unchanged
- this repair affects server-side result normalization only; it does not change
  Blender scene state, RPC/addon behavior, or deterministic truth authority
- broader typed projection or owner-seam cleanup is deferred to `TASK-166-06`
  and should not duplicate parser heuristics inside provider backends

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_result_types.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `poetry run pytest ./tests/unit`
