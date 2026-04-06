# TASK-140-01-02: Qwen Runtime Profile Vocabulary and Model-ID Routing

**Parent:** [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md)
**Depends On:** [TASK-140-01-01](./TASK-140-01-01_Docs_Reviewed_Qwen_Multimodal_Catalog_And_Product_Fit.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add the Qwen-specific runtime vocabulary and deterministic model-id routing
rules needed to resolve the correct `vision_contract_profile` for Qwen
families.

## Business Problem

Without a dedicated routing leaf, Qwen support will drift back into ad hoc
substring checks scattered across runtime, prompting, or parser code.

## Code Constraint

This leaf extends the contract-profile layer, not the provider layer.

- `VISION_EXTERNAL_PROVIDER` / `VisionExternalProviderName` stay:
  - `generic`
  - `openrouter`
  - `google_ai_studio`
- work in `server/infrastructure/config.py` and
  `server/adapters/mcp/vision/config.py` is limited to
  `VISION_EXTERNAL_CONTRACT_PROFILE` / `VisionContractProfile`
- work in `server/adapters/mcp/sampling/result_types.py` is limited to keeping
  `VisionAssistContract.vision_contract_profile` aligned with
  `VisionContractProfile`

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- Qwen-specific `vision_contract_profile` values are explicit and typed across:
  - `VisionContractProfile` runtime/config vocabulary and validators
  - public `VisionAssistContract.vision_contract_profile` result contracts
- model-id routing covers the docs-reviewed Qwen families intentionally
- explicit override precedence from `TASK-139` still wins over Qwen auto-match
- unknown or non-matching Qwen-family ids still fall back to `generic_full`
- Qwen family selection logic is centralized in runtime resolution, not
  duplicated across prompting/backend/parsing call sites
- `VISION_EXTERNAL_PROVIDER` vocabulary remains unchanged

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
