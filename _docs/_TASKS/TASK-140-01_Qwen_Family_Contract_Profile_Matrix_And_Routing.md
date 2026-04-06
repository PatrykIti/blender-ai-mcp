# TASK-140-01: Qwen Family Contract Profile Matrix and Routing

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Turn the current broad "Qwen accepts images" assumption into one explicit
family matrix for Qwen multimodal models, then route those families through
deterministic compare/document/exclusion profiles.

## Business Problem

The Qwen surface now spans several materially different multimodal lines:

- legacy `qwen-vl-plus` / `qwen-vl-max`
- Qwen2.5-VL
- Qwen3-VL
- newer adjacent multimodal lines that official docs position as stronger
  successors to older Qwen-VL variants
- OCR/document-oriented variants

Those families should not all inherit one silent generic profile. Some are
credible staged-compare candidates, some may want a stricter compare contract,
and some should be explicitly excluded from compare routing.

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- the repo has one explicit Qwen multimodal family matrix
- legacy `qwen-vl-plus` / `qwen-vl-max`, Qwen2.5-VL, and Qwen3-VL are not
  treated as one undifferentiated family
- any Qwen-specific `vision_contract_profile` values introduced by this slice
  stay typed in both runtime/config and public `VisionAssistContract` results
- document/OCR-oriented Qwen variants are either given a separate profile or
  explicitly excluded from compare routing
- runtime/profile selection can route Qwen families without re-parsing model
  ids ad hoc at every call site
- unknown or not-yet-classified Qwen-family ids still fall back to
  `generic_full` under the `TASK-139` precedence model

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-140-01-01](./TASK-140-01-01_Docs_Reviewed_Qwen_Multimodal_Catalog_And_Product_Fit.md) | Build the docs-reviewed Qwen family matrix and classify product fit before coding routing rules |
| 2 | [TASK-140-01-02](./TASK-140-01-02_Qwen_Runtime_Profile_Vocabulary_And_Model_ID_Routing.md) | Expand runtime profile vocabulary and deterministic model-id routing for Qwen families |
| 3 | [TASK-140-01-03](./TASK-140-01-03_Qwen_Compare_Document_And_Exclusion_Profiles.md) | Define the concrete Qwen compare/document/exclusion profile behavior in prompting, backend, and parsing layers |
