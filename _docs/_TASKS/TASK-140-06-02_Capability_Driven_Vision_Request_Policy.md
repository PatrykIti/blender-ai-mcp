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

## Implementation Notes

- keep this leaf focused on turning resolved capability data into bounded
  request-policy choices on the existing runtime/backend/prompting seams
- cover:
  - output budget selection
  - `json_schema` versus `json_object`
  - `response-healing` plugin use
  - reasoning-related parameters
  - modality gating
- preserve the existing precedence order: env override, live metadata,
  fallback registry, then conservative default behavior

## Runtime / Security Contract Notes

- capability-driven request policy must stay bounded and deterministic
- do not let provider-specific heuristics bypass the typed capability contract
- logs should explain the final request posture without exposing secrets

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

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_prompting.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-06`
- should close before diagnostics/closeout claim capability-aware policy is complete
