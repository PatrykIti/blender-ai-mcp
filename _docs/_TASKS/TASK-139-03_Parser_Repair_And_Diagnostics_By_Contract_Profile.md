# TASK-139-03: Parser, Repair, and Diagnostics by Vision Contract Profile

**Parent:** [TASK-139](./TASK-139_Model_Family_Specific_Vision_Contract_Profiles_For_External_Runtimes.md)
**Depends On:** [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Route output parsing, near-JSON repair, and diagnostics by the resolved vision
contract profile instead of only by provider name.

## Business Problem

The current parser already does the right thing by rejecting prose instead of
silently accepting it. The missing piece is contract-aware repair reuse.

Today:

- provider-specific near-JSON repair exists for Google AI Studio staged compare
- OpenRouter-hosted Google-family models cannot reuse it
- diagnostics say "no JSON" but do not yet tell the operator enough about
  vision-contract-profile mismatch risk

## Repository Touchpoints

- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- parsing/diagnostics accept the resolved `vision_contract_profile` as an input
- compare-flow repair logic can be reused by compatible profiles across
  providers
- operator-facing diagnostics preserve the current loud failure behavior while
  exposing more precise vision-contract-profile/context details

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-139-03-01](./TASK-139-03-01_Profile_Aware_Parse_And_Diagnose_Flow.md) | Thread the resolved `vision_contract_profile` through parser/diagnostic entry points |
| 2 | [TASK-139-03-02](./TASK-139-03-02_OpenRouter_Google_Family_Repair_And_Failure_Surface.md) | Reuse compare-flow repair behavior for OpenRouter Google-family vision contract profiles and tighten the failure surface |
