# TASK-140-06-04: Diagnostics, Harness, Docs, And Closeout For Model Capabilities

**Parent:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Close the capability-aware OpenRouter work by exposing operator diagnostics,
updating harness/docs, and recording validation/changelog results.

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
