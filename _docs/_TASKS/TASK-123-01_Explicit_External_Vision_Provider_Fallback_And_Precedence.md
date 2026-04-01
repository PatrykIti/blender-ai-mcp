# TASK-123-01: Explicit External Vision Provider Fallback and Precedence

**Parent:** [TASK-123](./TASK-123_Runtime_Reliability_Fixes_For_Vision_Provider_Startup_And_Task_Terminality.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-121-04](./TASK-121-04_Lightweight_Vision_Runtime_And_Evaluation.md)

**Completion Summary:** External vision runtime resolution now treats explicit provider selection as authoritative for profile choice while still letting model/auth values fall back from provider-specific env to generic `VISION_EXTERNAL_*` env. Unit coverage now proves startup works for explicit OpenRouter and Google AI Studio / Gemini selections that only populate the generic fallback model, and that explicit provider choice still wins over conflicting env from the other provider.

---

## Objective

Fix external vision runtime config resolution so an explicitly selected provider
decides the profile, while model/auth values may still come from either
provider-specific settings or the generic external fallback settings.

---

## Business Problem

The current runtime gate is too strict in the wrong place.

Today an explicit provider like `openrouter` or `google_ai_studio` can still
fail startup when only the generic fallback model is configured:

- `VISION_EXTERNAL_PROVIDER=openrouter`
- `VISION_EXTERNAL_MODEL=...`
- no `VISION_OPENROUTER_MODEL`

That is a valid and reasonable configuration, because the OpenRouter branch can
still derive:

- provider identity from `VISION_EXTERNAL_PROVIDER`
- default base URL from the provider profile
- model from `VISION_EXTERNAL_MODEL`

But the current pre-check never builds the external config in that case, so
typed runtime validation fails during startup.

---

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_VISION/README.md` if env precedence notes need to be clarified

---

## Implementation Direction

- treat explicit provider selection as enough to enter the matching external
  provider branch
- resolve `model`, `api_key`, and `api_key_env` in this order:
  - provider-specific value first
  - generic external fallback second
- keep provider-default base URLs for explicit OpenRouter and Google AI Studio
  / Gemini selections when no provider-specific base URL override is set
- preserve current generic external behavior when
  `VISION_EXTERNAL_PROVIDER=generic`
- keep explicit provider selection authoritative when conflicting env for the
  other provider also exists

---

## Acceptance Criteria

- explicit OpenRouter selection works with only `VISION_EXTERNAL_MODEL`
- explicit Google AI Studio / Gemini selection works with only
  `VISION_EXTERNAL_MODEL`
- conflicting opposite-provider env does not override an explicitly selected
  provider
- generic external behavior is not regressed

---

## Leaf Work Items

1. Runtime gate and precedence
   - remove the startup gate that depends on provider-specific model env being
     present when the provider is already explicit
   - make the selected provider control which config branch is built
2. Regression coverage
   - add unit coverage for explicit OpenRouter plus generic model fallback
   - add unit coverage for explicit Google AI Studio / Gemini plus generic
     model fallback
   - add unit coverage for explicit-provider precedence when the other
     provider's env is also populated
