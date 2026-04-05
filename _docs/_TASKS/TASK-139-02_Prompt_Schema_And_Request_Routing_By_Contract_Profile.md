# TASK-139-02: Prompt, Schema, and Request Routing by Contract Profile

**Parent:** [TASK-139](./TASK-139_Model_Family_Specific_Vision_Contract_Profiles_For_External_Runtimes.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Route prompt-building, JSON-schema selection, and external request payload
construction by resolved contract profile rather than only by transport
provider.

## Business Problem

Today the narrower compare contract is effectively a provider-specific Gemini
path. That is too coarse, because:

- the same transport/provider may host models with very different structured
  output behavior
- the same model family may appear behind different transports/providers
- provider-only gating prevents reuse of a known-good narrow contract path

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- prompt/schema routing no longer depends only on `provider_name`
- a resolved contract profile can drive the narrow compare contract on
  OpenRouter when appropriate
- request payload construction remains transport-correct while still using the
  selected prompt/schema profile

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-139-02-01](./TASK-139-02-01_Profile_Aware_Prompting_Abstraction.md) | Replace provider-only prompt/schema gating with contract-profile-aware helpers |
| 2 | [TASK-139-02-02](./TASK-139-02-02_External_Backend_Request_Routing_By_Contract_Profile.md) | Make backend request payload generation use the selected contract profile while preserving transport correctness |
