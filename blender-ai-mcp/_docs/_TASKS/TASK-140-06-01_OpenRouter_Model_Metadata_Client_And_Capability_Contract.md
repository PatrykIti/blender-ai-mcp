# TASK-140-06-01: OpenRouter Model Metadata Client And Capability Contract

**Parent:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Status:** ⏳ To Do
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
