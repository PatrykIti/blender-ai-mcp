# TASK-140-06-02: Capability-Driven Vision Request Policy

**Parent:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Completion Date:** 2026-06-23

## Objective

Use resolved OpenRouter model capabilities to choose the final vision request
policy instead of relying only on static env values and broad family-name
heuristics.

## Completion Summary

The shipped runtime now derives effective output-token caps from explicit
operator config, OpenRouter API/fallback model capability data, profile floors,
and fail-safe caps. The OpenRouter backend gates image/text modality support,
selects `json_schema`, `json_object`, or no response format from supported
parameters, enables response-healing through bounded policy, and logs the
resulting `last_request_policy_summary` with capability source, selected
contract profile, request mode, final requested tokens, provider preferences,
and plugin posture.

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

- closed under `TASK-140-06` during the `TASK-140-07` capability-first audit
- no runtime code changed in the audit pass; closure records already-shipped behavior
