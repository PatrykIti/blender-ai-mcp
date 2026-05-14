# TASK-140-03: OpenAI Image-Input Profiles and Structured Compare Policy

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Decide whether current OpenAI image-input families can keep reusing the
existing generic external profile or whether the repo needs one or more
OpenAI-specific compare profiles for stricter structured output behavior on
the existing shared external backend path.

## Business Problem

The runtime already has a generic external path that can talk to OpenAI-style
APIs, but `TASK-140` should not assume that "transport works" is the same as
"family-specific compare contract is correct".

## Backend Boundary

OpenAI-family work under this slice stays inside the current shared
`openai_compatible_external` backend seam.

- `google_ai_studio` remains the only dedicated transport/request branch
- OpenAI-family work does not add a new transport/provider branch
- backend changes, if needed, are limited to profile-aware request/schema
  behavior on the existing shared path

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

- OpenAI image-input families have an explicit profile/routing decision
- the task records whether GPT-4o, GPT-4.1, and smaller image-input tiers can
  share one profile or need separation
- if OpenAI-specific `vision_contract_profile` values are introduced, they are
  propagated through public `VisionAssistContract` typing rather than living
  only in runtime helpers
- unknown or non-matching OpenAI-family ids still fall back to `generic_full`
  under the `TASK-139` precedence model
- structured compare behavior for OpenAI families is evidence-driven rather
  than inherited accidentally from generic transport support
- backend changes, if needed, stay inside the shared
  `openai_compatible_external` path and do not become provider integration

## Implementation Notes

- keep this slice on the shared external backend path and use it to decide
  whether OpenAI image-input families truly need narrower compare profiles
- ground the work in:
  - `vision/runtime.py` for routing
  - `vision/prompting.py` and `vision/parsing.py` for structured compare
    behavior
  - `vision/backends.py` only when a profile-aware request/schema adjustment is
    required on the existing shared path
- let the current three physical leaves own:
  - routing and typed contract vocabulary
  - structured compare policy
  - regression and failure-surface proof

## Runtime / Security Contract Notes

- do not broaden this slice into OpenAI provider-integration work
- keep any new OpenAI-specific profile values typed end to end in public
  contract surfaces
- if the evidence shows `generic_full` remains correct, preserve that outcome
  explicitly instead of creating profile churn for its own sake

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
| 1 | [TASK-140-03-01](./TASK-140-03-01_OpenAI_Family_Routing_And_Typed_Contract_Vocabulary.md) | Add explicit OpenAI family routing and typed contract vocabulary without defaulting to a new provider alias |
| 2 | [TASK-140-03-02](./TASK-140-03-02_OpenAI_Structured_Compare_Contract_And_Strict_Output_Policy.md) | Decide whether OpenAI compare flows need a stricter profile than the current generic full contract |
| 3 | [TASK-140-03-03](./TASK-140-03-03_OpenAI_Family_Regression_Cases_And_Failure_Surface.md) | Lock the OpenAI family decisions with targeted regression and diagnostics expectations |

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_result_types.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140`
- should close only after all three physical child leaves land with aligned runtime/docs evidence
