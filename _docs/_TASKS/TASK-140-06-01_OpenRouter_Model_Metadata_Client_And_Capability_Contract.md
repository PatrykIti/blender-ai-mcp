# TASK-140-06-01: OpenRouter Model Metadata Client And Capability Contract

**Parent:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Add one bounded model-metadata lookup path for OpenRouter and normalize the
response into a typed capability contract that the vision runtime can consume.

The initial API source should be OpenRouter's model catalog endpoint, with the
runtime extracting fields such as model id, context length, modalities,
supported parameters, and provider output limits when present.

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/backends.py`
- `server/infrastructure/config.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Acceptance Criteria

- a typed capability model exists for at least:
  - model id
  - capability source
  - `context_length`
  - `max_completion_tokens`
  - input modalities
  - output modalities
  - supported parameters
  - raw provider/source metadata summary
- OpenRouter API lookup is bounded by timeout/error handling and does not block
  server startup unnecessarily
- missing/invalid model metadata degrades to `capability_source="unknown"` or
  fallback registry use instead of crashing normal guided sessions
- no API keys or secrets are logged

## Tests To Add/Update

- Unit:
  - fake OpenRouter catalog response with full fields
  - missing model id response
  - catalog request failure / timeout
  - malformed model metadata
- E2E:
  - optional live OpenRouter metadata smoke behind an explicit env flag

## Changelog Impact

- include in the TASK-140-06 changelog entry

## Completion Summary

- 2026-05-10: Added a bounded OpenRouter `/models` catalog resolver that
  normalizes live model metadata into the shared `VisionModelCapabilities`
  contract.
- The lookup runs lazily on the first OpenRouter-backed vision request, not
  during server startup.
- Live OpenRouter metadata now wins over reviewed fallback profiles when it is
  available; lookup failures, malformed catalog payloads, or missing model ids
  degrade to `capability_source="unknown"` or keep an existing fallback profile
  without crashing guided sessions.
- Capability summaries now carry a small non-secret `metadata_summary` with
  source/provider shape details for diagnostics and future request-policy work.

## Validation Results

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_openrouter_model_capabilities.py tests/unit/adapters/mcp/test_vision_external_backend.py::test_openrouter_api_metadata_overrides_fallback_capability_policy tests/unit/adapters/mcp/test_vision_external_backend.py::test_openrouter_metadata_failure_keeps_reviewed_fallback_policy -q`
  - passed, `6 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_external_backend.py -q`
  - passed, `16 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
  - passed, `42 passed`
- `poetry run ruff check server/adapters/mcp/vision/config.py server/adapters/mcp/vision/backends.py server/adapters/mcp/vision/openrouter_models.py server/adapters/mcp/vision/model_profiles/types.py tests/unit/adapters/mcp/test_openrouter_model_capabilities.py tests/unit/adapters/mcp/test_vision_external_backend.py`
  - passed
- `poetry run mypy`
  - passed, `Success: no issues found in 737 source files`
- `git diff --check`
  - passed
