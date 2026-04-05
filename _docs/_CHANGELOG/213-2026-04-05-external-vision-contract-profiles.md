# 213. External vision contract profiles

Date: 2026-04-05

## Summary

Decoupled external vision prompt/schema/parser behavior from provider-only
transport routing by introducing explicit `vision_contract_profile`
resolution for external runtimes.

## What Changed

- added one explicit `VISION_EXTERNAL_CONTRACT_PROFILE` env/config override
  plus typed `vision_contract_profile` fields in external vision runtime
  config/models
- implemented deterministic contract-profile resolution with this precedence:
  explicit override, Google-family model-id auto-match, provider default,
  generic fallback
- routed prompt/system/schema selection through the resolved contract profile
  instead of hard-coding the narrow compare path only to
  `provider_name == "google_ai_studio"`
- updated `OpenAICompatibleVisionBackend` to consume the prompt/schema seam
  while preserving OpenRouter and Google AI Studio transport-specific request
  branches
- threaded `vision_contract_profile` through parsing and diagnostics so
  compare-flow repair can be reused by OpenRouter-hosted Google-family models
  and failure text now exposes the resolved profile
- extended `VisionAssistContract` and harness output so operator-visible
  results can show the selected contract profile directly
- added focused unit coverage for runtime resolution, prompting, parsing, and
  backend routing plus a targeted `tests/e2e/vision/` end-to-end external
  compare-path regression
- updated harness/script/docs/task-board guidance so provider transport,
  contract profile override, auto-match behavior, and evidence types are all
  described consistently

## Why

OpenRouter-hosted Google-family models needed to reuse the narrow staged
compare contract and repair path without being forced onto the Google AI
Studio transport branch. Provider identity alone was too coarse for reliable
external compare behavior.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_external_backend.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py tests/e2e/vision/test_external_contract_profile_compare_path.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_reference_images.py -q`
