# 338. TASK-140-06 OpenRouter model metadata client

Date: 2026-05-10

Task: `TASK-140-06-01`

## Summary

Added the first API-first OpenRouter model capability lookup slice for the
external vision runtime.

## Changes

- Added a bounded OpenRouter model-catalog resolver for `/api/v1/models`.
- Normalized live catalog fields into `VisionModelCapabilities`, including
  context length, top-provider max completion tokens, modalities, supported
  parameters, and a small non-secret metadata summary.
- Made OpenRouter-backed vision requests refresh model capabilities lazily on
  the first request, so server startup stays independent of catalog
  availability.
- Preserved reviewed fallback profiles when the catalog is unavailable,
  malformed, or missing the selected model id.
- Updated TASK and vision/MCP docs for the API-first capability precedence.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_openrouter_model_capabilities.py tests/unit/adapters/mcp/test_vision_external_backend.py::test_openrouter_api_metadata_overrides_fallback_capability_policy tests/unit/adapters/mcp/test_vision_external_backend.py::test_openrouter_metadata_failure_keeps_reviewed_fallback_policy -q` (`6 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_external_backend.py -q` (`16 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q` (`42 passed`)
- `poetry run ruff check server/adapters/mcp/vision/config.py server/adapters/mcp/vision/backends.py server/adapters/mcp/vision/openrouter_models.py server/adapters/mcp/vision/model_profiles/types.py tests/unit/adapters/mcp/test_openrouter_model_capabilities.py tests/unit/adapters/mcp/test_vision_external_backend.py`
- `poetry run mypy` (`Success: no issues found in 737 source files`)
- `git diff --check`
