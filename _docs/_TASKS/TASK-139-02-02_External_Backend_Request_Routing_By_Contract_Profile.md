# TASK-139-02-02: External Backend Request Routing by Contract Profile

**Parent:** [TASK-139-02](./TASK-139-02_Prompt_Schema_And_Request_Routing_By_Contract_Profile.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make `OpenAICompatibleVisionBackend` build provider-correct requests while still
using the resolved contract profile for prompt/schema behavior.

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

## Repository Touchpoints

- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Acceptance Criteria

- request transport remains correct for OpenRouter and Google AI Studio
- selected contract profile can alter prompt/schema content without forcing a
  different transport branch
- OpenRouter Google-family compare flows can use the narrower compare contract
  where selected

## Leaf Work Items

- route `build_vision_payload_text(...)`, `build_vision_system_prompt(...)`, and
  `build_vision_response_json_schema(...)` through the resolved profile
- keep provider-specific auth/header behavior unchanged
- add external-backend regression tests for OpenRouter + Google-family compare
  flows

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped
