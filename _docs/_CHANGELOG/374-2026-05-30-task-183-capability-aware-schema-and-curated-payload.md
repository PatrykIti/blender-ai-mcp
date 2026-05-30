# 374. TASK-183 capability-aware schema and curated payload

Date: 2026-05-30

## Summary

Implemented the core of `TASK-183` (subtask `TASK-183-01`): the vision response
schema is now capability-aware (the additive structured `findings` channel is
dropped for models that do not support structured outputs, keeping a leaner
contract), and the default external payload no longer leaks internal plumbing
identifiers. This also fixes a real gap surfaced while wiring the capability
gate: the external/local backend normalization was dropping the `findings`
(TASK-178) and `evidence_truncated`/`omitted_count`/`analysis_unusable`
(TASK-176) fields before they reached the result contract.

## Changes

- `server/adapters/mcp/vision/backends.py`: `_normalize_assist_payload` now passes
  through `findings`, `evidence_truncated`, `omitted_count`, and
  `analysis_unusable`, so the TASK-176/178 signals actually reach
  `VisionAssistContract` in the real backend path (previously silently dropped).
  Added `_include_structured_findings()` (capability check) and wired it into all
  three `build_vision_response_json_schema` call sites.
- `server/adapters/mcp/vision/prompting.py`: `build_vision_response_json_schema`
  gained an `include_findings` flag and a `_maybe_strip_findings` helper that
  keeps `properties`/`required` in sync for strict providers when the channel is
  dropped; the default external payload now strips internal plumbing keys
  (`bundle_id`, `goal_id`, `preset_names`, packet identifiers) via
  `_sanitized_request_metadata`.

## Tests

- `tests/unit/adapters/mcp/test_vision_external_backend.py`: structured findings
  (with `defect_id`) and truncation signals survive backend normalization; the
  capability gate drops the findings schema for weak models
- `tests/unit/adapters/mcp/test_vision_prompting.py`: internal IDs are stripped
  from the default payload
- full `poetry run pytest ./tests/unit` green; `ruff` and `mypy` clean

## Follow-on

`TASK-183-02` (deterministic render-vs-reference consistency cross-check and
silhouette severity-threshold calibration) remains open; it touches `silhouette.py`
metric thresholds and an optional heavy embedding variant, and warrants its own
calibration + regression-fixture pass.

## Research Basis

3DGen-Bench (arXiv:2503.21745), GPTEval3D (arXiv:2401.04092): richer per-criterion
schemas help capable models; weak models benefit from leaner contracts. Re-measure
on `tests/fixtures/vision_eval` before claiming gains.
