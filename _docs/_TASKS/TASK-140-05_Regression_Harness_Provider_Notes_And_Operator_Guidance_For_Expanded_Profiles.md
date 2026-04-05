# TASK-140-05: Regression Harness, Provider Notes, and Operator Guidance for Expanded Profiles

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Depends On:** [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md), [TASK-140-02](./TASK-140-02_Anthropic_Claude_Vision_Profiles_And_Transport_Integration.md), [TASK-140-03](./TASK-140-03_OpenAI_Image_Input_Profiles_And_Structured_Compare_Policy.md), [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Keep automated coverage, harness evidence, provider notes, `.env.example`,
launcher scripts, and MCP client examples aligned with the broader external
profile matrix from `TASK-140`.

## Business Problem

This umbrella will only stay trustworthy if the evidence/documentation side
keeps pace with the runtime matrix. Otherwise the repo will repeat the old
drift where transport support exists but docs and operator notes do not say
which contract/profile assumptions actually hold.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/e2e/vision/`
- `scripts/vision_harness.py`
- `scripts/run_streamable_openrouter.sh`
- `.env.example`
- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- every promoted family/profile decision has matching automated coverage
- harness output and docs expose the selected `vision_contract_profile`
- provider notes distinguish docs-reviewed support, harness evidence, and
  operator-reported behavior
- `.env.example`, launcher scripts, and MCP client examples reflect the same
  profile matrix as runtime/docs

## Docs To Update

- `.env.example`
- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/scripts/test_script_tooling.py`
- targeted `tests/e2e/vision/`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-140-05-01](./TASK-140-05-01_Automated_Coverage_And_Harness_Scenario_Expansion.md) | Expand automated regression and harness scenarios to cover the broader external family matrix |
| 2 | [TASK-140-05-02](./TASK-140-05-02_Provider_Notes_Env_Example_And_Launcher_Client_Config_Alignment.md) | Keep docs, `.env.example`, launch helpers, and client configs aligned with the expanded profile matrix |
| 3 | [TASK-140-05-03](./TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md) | Formalize the evidence model so support and promotion decisions stay reproducible |
