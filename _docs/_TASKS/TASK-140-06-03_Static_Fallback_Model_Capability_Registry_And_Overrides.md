# TASK-140-06-03: Static Fallback Model Capability Registry And Overrides

**Parent:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add a small local fallback registry for known model capabilities and define
operator override precedence, without turning the registry into the primary
source of truth.

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/config.py`
- `server/infrastructure/config.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `.env.example`

## Acceptance Criteria

- fallback registry includes only explicitly reviewed model ids or family
  patterns, with source/last-reviewed metadata
- initial fallback entries cover the specific model families currently used by
  operators, such as:
  - `openai/gpt-5.4-nano`
  - current OpenRouter Google-family ids used in tests
  - current Qwen ids used in docs/harness notes
- fallback values include at least context length, max output, modalities, and
  structured-output parameter posture when known
- precedence is explicit:
  - env override
  - OpenRouter API data
  - local fallback registry
  - unknown/default conservative policy
- docs warn that fallback data can drift and must not be treated as stronger
  than live OpenRouter metadata

## Tests To Add/Update

- Unit:
  - fallback registry used when OpenRouter metadata is unavailable
  - live metadata overrides stale fallback
  - env override beats both API and fallback
  - unknown model falls back to conservative request budget

## Changelog Impact

- include in the TASK-140-06 changelog entry
