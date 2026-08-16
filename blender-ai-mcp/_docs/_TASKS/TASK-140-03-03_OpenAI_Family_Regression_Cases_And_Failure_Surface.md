# TASK-140-03-03: OpenAI Family Regression Cases and Failure Surface

**Parent:** [TASK-140-03](./TASK-140-03_OpenAI_Image_Input_Profiles_And_Structured_Compare_Policy.md)
**Depends On:** [TASK-140-03-02](./TASK-140-03-02_OpenAI_Structured_Compare_Contract_And_Strict_Output_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Lock the OpenAI profile decisions behind targeted regression cases and a clear
diagnostic/error surface so support decisions stay reproducible.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- OpenAI family routing has targeted automated coverage
- diagnostics expose the selected `vision_contract_profile` on OpenAI compare
  failures too
- the repo can distinguish "supported by transport" from "supported as a
  staged compare default"

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- targeted `tests/e2e/vision/`

## Changelog Impact

- include in the parent slice changelog entry when shipped
