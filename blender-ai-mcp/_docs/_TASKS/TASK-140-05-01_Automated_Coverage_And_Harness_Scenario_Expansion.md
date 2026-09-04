# TASK-140-05-01: Automated Coverage and Harness Scenario Expansion

**Parent:** [TASK-140-05](./TASK-140-05_Regression_Harness_Provider_Notes_And_Operator_Guidance_For_Expanded_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Expand unit and targeted end-to-end coverage so each promoted external family
decision under `TASK-140` is backed by repeatable automated evidence.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `tests/e2e/vision/`
- `scripts/vision_harness.py`

## Acceptance Criteria

- each supported family/profile combination has targeted runtime/prompt/parser/
  backend regression coverage
- profile-vocabulary expansion is covered through public result-contract tests,
  not only runtime-selection tests
- harness scenarios distinguish simple checkpoint compare from richer assembled
  loops when that difference matters
- unsupported/excluded families also have negative-path coverage where useful

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- targeted `tests/e2e/vision/`

## Changelog Impact

- include in the parent slice changelog entry when shipped
