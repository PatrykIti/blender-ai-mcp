# TASK-140-06-04: Diagnostics, Harness, Docs, And Closeout For Model Capabilities

**Parent:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Status:** ✅ Done
**Priority:** 🟠 High
**Completion Date:** 2026-06-23

## Objective

Close the capability-aware OpenRouter work by exposing operator diagnostics,
updating harness/docs, and recording validation/changelog results.

## Completion Summary

The shipped result contract exposes `VisionCapabilitySummaryContract` on
`VisionAssistContract`, and the runner builds it from resolved model
capabilities, request-policy summary, token usage, and finish reason. The vision
harness records a bounded `capability_summary` plus diagnostics for external
runs, and `_docs/_VISION/README.md` / `_docs/_MCP_SERVER/README.md` now describe
OpenRouter API-first metadata, fallback precedence, request policy diagnostics,
and model-capability-gated Set-of-Mark behavior.

Audit caveat: the runner path refreshes its runtime from the backend after lazy
OpenRouter metadata lookup before building the public summary. Standalone
harness promotion work should keep checking live-only metadata summary behavior
under `TASK-187` before using it as promotion evidence.

## Repository Touchpoints

- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `tests/e2e/vision/`
- `scripts/vision_harness.py`
- `scripts/run_streamable_openrouter.sh`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- `VisionAssistContract` or adjacent diagnostics expose the resolved capability
  summary in a bounded form
- logs show:
  - model id
  - capability source
  - model max input/output where known
  - final request `max_tokens`
  - selected contract profile and request mode
- `scripts/vision_harness.py` can record capability diagnostics for OpenRouter
  model runs
- docs explain how to interpret OpenRouter API data versus fallback registry
  versus env overrides
- TASK-140-06 descendants are closed consistently and the changelog is indexed

## Implementation Notes

- use this leaf to expose the capability-aware runtime in bounded operator
  diagnostics, harness output, and closeout docs
- keep diagnostics aligned across:
  - runtime/result contracts
  - logs
  - `scripts/vision_harness.py`
  - docs/changelog closeout
- close the family only after the already-landed metadata/fallback leaves and
  the request-policy leaf point at one coherent capability story

## Runtime / Security Contract Notes

- diagnostics must remain non-secret and bounded in size
- harness output should explain capability source and request cap without
  dumping raw provider payloads unnecessarily
- docs must keep API-first metadata, fallback registry, and env override
  precedence explicit

## Tests To Add/Update

- Unit:
  - result-contract diagnostics stay bounded and non-secret
  - logging includes capability source and final token cap
  - harness output records capability source
- E2E:
  - optional live OpenRouter metadata/capability smoke behind an explicit env
    flag and API key

## Changelog Impact

- add and index a dedicated `_docs/_CHANGELOG/*` entry during closeout

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_result_types.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- opt-in OpenRouter live capability smoke under `tests/e2e/vision/` when
  explicit env flags and API keys are available

## Status / Board Update

- closed under `TASK-140-06` during the `TASK-140-07` capability-first audit
- no runtime code changed in the audit pass; closure records already-shipped behavior
