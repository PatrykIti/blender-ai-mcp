# TASK-121-04-01-04: Google AI Studio Gemini Vision Path

**Parent:** [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

Added a supported Google AI Studio / Gemini path for the vision module so users
can plug in an API key, select Gemini multimodal models, and compare their
bounded vision quality/cost profile against the local and other external paths.

## Objective

Support Gemini as another pluggable remote provider for bounded vision work,
with explicit setup/docs for:

- Google AI Studio API key wiring
- model selection
- timeout/token budgeting
- smoke/eval comparison against current baselines

## Implementation Direction

- keep Gemini behind the same bounded external-runtime contract used by other
  remote providers
- prefer config that makes provider switching easy at runtime
- document at least one recommended low-cost multimodal model path for
  experimentation
- add provider-specific diagnostics so quota/auth/model errors are not masked
  as generic external-runtime failures
- capture governance notes around free-tier limits and model drift risk

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

- dedicated Gemini env/config aliases now exist for:
  - model
  - API key / API key env var
  - optional base URL override
- Google AI Studio now runs through the bounded external-runtime path using
  provider-specific:
  - endpoint construction
  - payload shape
  - response parsing
  - API key header handling
- `scripts/vision_harness.py` now supports Gemini-oriented flags
- unit coverage exists for:
  - runtime config alias resolution
  - provider-specific request/response handling
  - harness config wiring
