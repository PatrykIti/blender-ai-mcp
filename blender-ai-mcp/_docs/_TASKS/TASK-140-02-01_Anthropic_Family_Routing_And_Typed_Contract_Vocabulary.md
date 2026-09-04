# TASK-140-02-01: Anthropic Family Routing and Typed Contract Vocabulary

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Family_Contracts_On_The_Existing_Provider_Surface.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add the model-id/family-routing and typed contract vocabulary needed to
resolve Claude-specific `vision_contract_profile` values on the existing
provider surface, without introducing a dedicated Anthropic provider by
default.

## Code Constraint

This leaf may extend contract-profile typing, but it does not extend provider
typing.

- `VISION_EXTERNAL_PROVIDER` / `VisionExternalProviderName` stay:
  - `generic`
  - `openrouter`
  - `google_ai_studio`
- changes in `server/infrastructure/config.py` and
  `server/adapters/mcp/vision/config.py` are limited to
  `VISION_EXTERNAL_CONTRACT_PROFILE` / `VisionContractProfile`
- changes in `server/adapters/mcp/sampling/result_types.py` are limited to
  keeping `VisionAssistContract.vision_contract_profile` aligned with
  `VisionContractProfile`

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `.env.example`

## Acceptance Criteria

- Anthropic / Claude family-routing vocabulary is explicit
- typed runtime config and public `VisionAssistContract` result contracts can
  expose any Claude-specific `vision_contract_profile` cleanly
- config precedence remains deterministic and compatible with `TASK-139`
- unknown or non-matching Claude-family ids still fall back to `generic_full`
- `VISION_EXTERNAL_PROVIDER` vocabulary remains unchanged
- this slice does not require a first-class Anthropic provider alias or
  provider enum expansion; if the current provider surface is insufficient,
  record that as follow-on work instead

## Docs To Update

- `.env.example`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
