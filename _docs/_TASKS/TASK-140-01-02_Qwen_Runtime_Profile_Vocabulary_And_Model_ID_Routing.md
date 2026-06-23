# TASK-140-01-02: Qwen Runtime Profile Vocabulary and Model-ID Routing

**Parent:** [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md)
**Depends On:** [TASK-140-01-01](./TASK-140-01-01_Docs_Reviewed_Qwen_Multimodal_Catalog_And_Product_Fit.md)
**Status:** ⏭️ Superseded
**Priority:** 🔴 High
**Superseded By:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Superseded Reason:** Replaced by the capability-first OpenRouter metadata, fallback capability registry, and request-policy model. Family-specific profiles return under `TASK-187` only when harness/operator evidence shows a real contract delta.

## Objective

Add the Qwen-specific runtime vocabulary and deterministic model-id routing
rules needed to resolve the correct `vision_contract_profile` for Qwen
families, especially for OpenRouter-hosted Qwen model ids that should no
longer collapse into one generic external bucket.

## Business Problem

Without a dedicated routing leaf, Qwen support will drift back into ad hoc
substring checks scattered across runtime, prompting, or parser code.

This leaf is the core mechanical continuation of `TASK-139`: the same
contract-selection seam now needs explicit Qwen family matching instead of one
coarse generic fallback for all Qwen multimodal variants.

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
- model-id routing covers the docs-reviewed Qwen families intentionally,
  especially on the OpenRouter-hosted ids we want to evaluate first
- explicit override precedence from `TASK-139` still wins over Qwen auto-match
- unknown or non-matching Qwen-family ids still fall back to `generic_full`
- Qwen family selection logic is centralized in runtime resolution, not
  duplicated across prompting/backend/parsing call sites
- `VISION_EXTERNAL_PROVIDER` vocabulary remains unchanged
- this leaf preserves the same architectural shape introduced in `TASK-139`:
  explicit override, deterministic family match, then fallback to
  `generic_full`

## Implementation Notes

- keep routing ownership centralized in `vision/runtime.py` and
  `VisionContractProfile` typing rather than scattering Qwen-family checks
  across prompting/backend/parsing call sites
- let the docs-reviewed matrix from `TASK-140-01-01` drive the family ids and
  aliases this leaf recognizes
- preserve the `TASK-139` precedence order: explicit override, deterministic
  family match, then `generic_full`

## Runtime / Security Contract Notes

- do not widen `VISION_EXTERNAL_PROVIDER` vocabulary here
- keep newly introduced Qwen profile values typed in both config/runtime and
  public result contracts
- unknown Qwen-family ids must degrade to the existing fallback instead of
  permissive ad hoc matches

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_result_types.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-01`
- should close before prompting/backend/parsing leaves start depending on new
  Qwen profile ids
