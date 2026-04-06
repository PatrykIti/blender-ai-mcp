# TASK-140-04-02: Selected NVIDIA Family Routing and Compare Path

**Parent:** [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md)
**Depends On:** [TASK-140-04-01](./TASK-140-04-01_NVIDIA_VLM_Family_Triage_Compare_Vs_Document_And_Retrieval.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Implement the runtime/config/backend routing for the NVIDIA compare-capable
subset on the existing provider surface only, without broadening support
to unrelated NVIDIA visual model classes.

## Code Constraint

This leaf operates on family/profile routing within the current provider and
result-contract inventory.

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
- backend changes stay inside the current `openai_compatible_external` path;
  this leaf does not add a provider-specific transport branch

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `.env.example`

## Acceptance Criteria

- the selected NVIDIA compare subset has one explicit family/profile routing
  story on the current provider surface
- request assumptions are validated for that path
- runtime selection does not imply support for excluded NVIDIA visual families
- unknown or non-matching NVIDIA-family ids still fall back to `generic_full`
- `VISION_EXTERNAL_PROVIDER` vocabulary remains unchanged
- this slice does not assume a new NVIDIA-specific provider branch or provider
  enum expansion; if the current provider surface is insufficient, record that
  as follow-on work instead
- any newly introduced NVIDIA-specific `vision_contract_profile` values remain
  typed in public `VisionAssistContract.vision_contract_profile` result surfaces

## Docs To Update

- `.env.example`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
