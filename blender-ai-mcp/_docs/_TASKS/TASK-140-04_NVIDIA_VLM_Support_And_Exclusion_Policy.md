# TASK-140-04: NVIDIA VLM Support and Exclusion Policy

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add an intentional NVIDIA VLM policy that distinguishes compare-capable
generative vision-language models from NVIDIA document/retrieval visual models
that should not silently enter staged compare flows on the existing shared
external backend path.

## Business Problem

The NVIDIA ecosystem contains several visually oriented model types:

- generative/reasoning VLMs
- document parsers
- retrieval/embedding/reranking-oriented models

This repo should not blur those classes together just because they all accept
images.

## Backend Boundary

NVIDIA-family work under `TASK-140` stays inside the current shared
`openai_compatible_external` backend seam.

- `google_ai_studio` remains the only dedicated transport/request branch
- NVIDIA-family work does not add a new provider/transport branch
- backend changes, if needed, stay limited to shared-path request/schema
  behavior plus profile-driven diagnostics

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- NVIDIA compare-capable versus non-compare-capable families are explicit
- document/retrieval visual models are not silently treated as compare backends
- only the selected NVIDIA compare-suitable subset is considered for runtime
  routing on the existing shared external backend path
- if NVIDIA-specific `vision_contract_profile` values are introduced, they are
  typed in public `VisionAssistContract` result surfaces
- unknown or non-matching NVIDIA-family ids still fall back to `generic_full`
  under the `TASK-139` precedence model
- backend changes, if needed, stay inside the shared
  `openai_compatible_external` path and do not become NVIDIA provider
  integration

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-140-04-01](./TASK-140-04-01_NVIDIA_VLM_Family_Triage_Compare_Vs_Document_And_Retrieval.md) | Build the docs-reviewed NVIDIA VLM triage matrix |
| 2 | [TASK-140-04-02](./TASK-140-04-02_Selected_NVIDIA_Family_Routing_And_Compare_Path.md) | Add family/profile routing only for the selected compare-capable NVIDIA subset on the existing provider surface |
| 3 | [TASK-140-04-03](./TASK-140-04-03_NVIDIA_Non_Compare_Exclusion_Contracts_And_Diagnostics.md) | Make exclusions and diagnostics explicit so non-compare NVIDIA models are not mistaken for supported compare paths |
