# TASK-121-04-01-03: OpenRouter Model Catalog and API-Key Path

**Parent:** [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

Add first-class OpenRouter support for the vision module so users can provide
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

## Acceptance Criteria

- a user can configure an OpenRouter API key and model id without code edits
- the vision layer can call OpenRouter through the bounded external-runtime path
- smoke tests/docs explain how to select and validate OpenRouter vision models
