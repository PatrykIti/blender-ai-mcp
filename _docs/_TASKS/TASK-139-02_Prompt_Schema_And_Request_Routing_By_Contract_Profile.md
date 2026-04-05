# TASK-139-02: Prompt, Schema, and Request Routing by Vision Contract Profile

**Parent:** [TASK-139](./TASK-139_Model_Family_Specific_Vision_Contract_Profiles_For_External_Runtimes.md)
**Depends On:** [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Prompt/system/schema selection is now driven by the
resolved `vision_contract_profile` plus request kind, and the external backend
consumes that seam while preserving provider-correct transport branches.

## Objective

Route prompt-building, JSON-schema selection, and external request payload
construction by the resolved vision contract profile rather than only by
transport provider.

## Business Problem

Today the narrower compare contract is effectively a provider-specific Gemini
path. That is too coarse, because:

- the same transport/provider may host models with very different structured
  output behavior
- the same model family may appear behind different transports/providers
- provider-only gating prevents reuse of a known-good narrow contract path

This slice therefore needs two distinct implementation seams:

- one prompt/schema ownership seam in `prompting.py`
- one backend request-assembly seam in `backends.py` that consumes the selected
  profile without re-owning prompt helper design

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- prompt/schema routing no longer depends only on `provider_name`
- a resolved `vision_contract_profile` can drive the narrow compare contract on
  OpenRouter when appropriate
- request payload construction remains transport-correct while still using the
  selected vision-contract-profile prompt/schema behavior

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
| 1 | [TASK-139-02-01](./TASK-139-02-01_Profile_Aware_Prompting_Abstraction.md) | Define and own the vision-contract-profile-aware prompt/schema helper seam in `prompting.py`, including prompt-specific regression coverage |
| 2 | [TASK-139-02-02](./TASK-139-02-02_External_Backend_Request_Routing_By_Contract_Profile.md) | Consume that seam from `backends.py` so request payload generation stays transport-correct while using the selected vision contract profile |
