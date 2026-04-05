# TASK-139-02-02: External Backend Request Routing by Vision Contract Profile

**Parent:** [TASK-139-02](./TASK-139-02_Prompt_Schema_And_Request_Routing_By_Contract_Profile.md)
**Depends On:** [TASK-139-02-01](./TASK-139-02-01_Profile_Aware_Prompting_Abstraction.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make `OpenAICompatibleVisionBackend` preserve provider-correct request
transport while consuming the already-defined vision-contract-profile-aware
prompting seam from `TASK-139-02-01`.

## Business Problem

There are two different concerns in the external backend:

- transport shape:
  - OpenRouter chat/completions
  - Google AI Studio generateContent
- contract shape:
  - generic full vision contract profile
  - narrow compare vision contract profile
  - future vision-contract-profile variants

Today those two concerns are partially conflated, which blocks reuse of the
better compare contract on other transports.

The ownership split for this leaf is deliberate:

- `server/adapters/mcp/vision/prompting.py` is owned by `TASK-139-02-01`
  and defines the prompt/schema selection seam
- `server/adapters/mcp/vision/backends.py` is owned here and must pass the
  resolved `vision_contract_profile` into that existing seam without
  redefining helper-selection policy

If this leaf re-opens prompt helper design, the two children become ambiguous
again and either one could be marked done incorrectly.

## Repository Touchpoints

- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Acceptance Criteria

- request transport remains correct for OpenRouter and Google AI Studio
- selected `vision_contract_profile` can alter prompt/schema content without
  forcing a different transport branch
- backend request assembly consumes the prompt/schema seam defined by
  `TASK-139-02-01` instead of re-owning prompt helper selection
- OpenRouter Google-family compare flows can use the narrower compare contract
  where selected

## Leaf Work Items

- route `build_vision_payload_text(...)`, `build_vision_system_prompt(...)`,
  and `build_vision_response_json_schema(...)` through the resolved
  `vision_contract_profile` at the backend request-assembly call sites
- keep provider-specific auth/header behavior unchanged
- add external-backend regression tests for OpenRouter + Google-family compare
  flows

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent prompt/schema slice unless this leaf is
  promoted independently
- when this leaf closes, update the parent task summary so the backend-vs-
  prompting responsibility split is recorded explicitly and the leaf is scoped
  as backend plumbing plus transport regressions only
