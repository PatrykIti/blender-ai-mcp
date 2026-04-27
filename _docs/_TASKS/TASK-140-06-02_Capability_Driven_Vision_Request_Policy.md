# TASK-140-06-02: Capability-Driven Vision Request Policy

**Parent:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Use resolved OpenRouter model capabilities to choose the final vision request
policy instead of relying only on static env values and broad family-name
heuristics.

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/runner.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`

## Acceptance Criteria

- final request `max_tokens` is derived from:
  - explicit env override, when present
  - model/provider max completion tokens, when known
  - contract-profile defaults and safety caps
  - static fallback registry, when API metadata is missing
- model capabilities influence whether the runtime sends:
  - `json_schema`
  - `json_object`
  - response-healing plugin
  - reasoning-related parameters
  - strict structured output
- image modalities are checked before sending image payloads when capability
  data is available
- the final decision is logged with the selected capability source and request
  cap

## Tests To Add/Update

- Unit:
  - OpenAI-family large-output model selects a larger bounded output cap for
    stage compare than the old static `600` default
  - unsupported `json_schema` falls back to a safe contract/request mode
  - missing image modality blocks or downgrades with an actionable diagnostic
  - explicit env override still wins over dynamic metadata
- E2E:
  - optional live OpenRouter run that records model capability diagnostics

## Changelog Impact

- include in the TASK-140-06 changelog entry
