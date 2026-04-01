# TASK-121-04-01-03: OpenRouter Model Catalog and API-Key Path

**Parent:** [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

Added first-class OpenRouter support for the vision module so users can provide
an `openrouter.ai` API key, choose remote multimodal models there, and run them
through the bounded vision contract without changing the MCP-facing surface.

## Objective

Make OpenRouter a supported remote provider path for vision-assisted modeling,
with explicit config/docs for:

- API key wiring
- base URL / provider identity
- model selection
- safe budget/timeout defaults

## Implementation Direction

- keep OpenRouter behind the existing pluggable external-runtime boundary
- do not fork the public `vision_assistant` contract just because the upstream
  vendor is OpenRouter
- add explicit config/env vars for:
  - API key
  - base URL defaulting to OpenRouter
  - model id
- document recommended model-selection patterns for multimodal use
- add smoke coverage and provider-specific diagnostics so failures are easy to
  distinguish from generic external-runtime failures

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/backends.py`
- `scripts/vision_harness.py`
- `_docs/_VISION/`
- `_docs/_DEV/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/vision/`

## Delivered

- OpenRouter can now be selected through the existing
  `openai_compatible_external` provider path
- dedicated env/config aliases now exist for:
  - model
  - API key
  - API key env var
  - optional site URL / site name headers
- OpenRouter defaults to `https://openrouter.ai/api/v1`
- `scripts/vision_harness.py` now accepts OpenRouter-specific flags
- unit coverage exists for:
  - runtime config alias resolution
  - provider-specific request headers
  - harness config wiring
