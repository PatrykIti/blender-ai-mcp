# TASK-139-02-02: External Backend Request Routing by Contract Profile

**Parent:** [TASK-139-02](./TASK-139-02_Prompt_Schema_And_Request_Routing_By_Contract_Profile.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make `OpenAICompatibleVisionBackend` preserve provider-correct request
transport while threading the resolved contract profile into the
prompt/schema-selection helpers that shape the request content.

## Business Problem

There are two different concerns in the external backend:

- transport shape:
  - OpenRouter chat/completions
  - Google AI Studio generateContent
- contract shape:
  - generic full compare contract
  - narrow compare contract
  - future profile variants

Today those two concerns are partially conflated, which blocks reuse of the
better compare contract on other transports.

The implementation seam also spans more than the backend module itself:

- `server/adapters/mcp/vision/prompting.py` owns the prompt, payload-text, and
  response-schema helper gates
- `server/adapters/mcp/vision/backends.py` owns transport assembly and must
  pass the resolved profile into those helpers instead of leaving the contract
  decision implicit

If this leaf only tracks backend transport code, it can be closed without
updating the real contract-selection seam.

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Acceptance Criteria

- request transport remains correct for OpenRouter and Google AI Studio
- selected contract profile can alter prompt/schema content without forcing a
  different transport branch
- prompt/schema helper routing is updated at the real selection seam in
  `prompting.py`, not only at the backend call site
- OpenRouter Google-family compare flows can use the narrower compare contract
  where selected

## Leaf Work Items

- route `build_vision_payload_text(...)`, `build_vision_system_prompt(...)`,
  and `build_vision_response_json_schema(...)` through the resolved profile at
  the `prompting.py` helper seam and at the backend request-assembly call sites
- keep provider-specific auth/header behavior unchanged
- add prompting-level coverage for profile-aware narrow compare routing
- add external-backend regression tests for OpenRouter + Google-family compare
  flows

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent prompt/schema slice unless this leaf is
  promoted independently
- when this leaf closes, update the parent task summary so the backend-vs-
  prompting responsibility split is recorded explicitly
