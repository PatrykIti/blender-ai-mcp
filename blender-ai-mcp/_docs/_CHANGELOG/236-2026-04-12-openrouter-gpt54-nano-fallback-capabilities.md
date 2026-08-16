# 236. OpenRouter GPT-5.4 Nano fallback capabilities

Date: 2026-04-12

## Summary

Added a first local fallback capability entry for `openai/gpt-5.4-nano` on the
OpenRouter vision path so the runtime can avoid treating a small static
`VISION_MAX_TOKENS` value as the model's actual output limit.

## What Changed

- added a typed `VisionModelCapabilities` contract for bounded runtime
  capability diagnostics
- added a fallback registry entry for `openai/gpt-5.4-nano` with:
  - `context_length=400000`
  - `max_completion_tokens=128000`
  - `text` + `image` input modalities
  - `text` output modality
  - structured-output parameter hints
- added `VisionRuntimeConfig.effective_max_tokens` so known large-output
  OpenRouter models can request a safer checkpoint output cap, currently
  raising the `openai/gpt-5.4-nano` compare path from the static 600-token env
  cap to a bounded 4096-token effective cap
- extended external vision request logging with:
  - `effective_max_tokens`
  - capability source
  - model context/output limits where known
  - model input modalities and supported parameters
- documented that this fallback is secondary to the planned OpenRouter API
  metadata resolver under TASK-140-06

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
  - result on this machine: `43 passed`
- `poetry run ruff check server/adapters/mcp/vision/config.py server/adapters/mcp/vision/runtime.py server/adapters/mcp/vision/backends.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py`
  - result on this machine: passed
