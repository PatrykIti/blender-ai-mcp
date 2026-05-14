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

## Implementation Notes

- use this leaf to lock the chosen OpenAI routing/profile behavior behind
  repeatable regression cases and operator-facing failure diagnostics
- keep targeted `tests/e2e/vision/` evidence aligned with the unit/runtime
  owner lanes instead of inventing a separate support matrix
- make failure reporting explicit enough that operators can tell whether they
  hit transport support, contract support, or a structured-output boundary

## Runtime / Security Contract Notes

- diagnostics must remain bounded and should not expose raw secrets or full
  provider payloads
- negative-path coverage should make unsupported structured-compare behavior
  obvious instead of silently degrading to generic success

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- targeted `tests/e2e/vision/`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-03`
- should close only after the OpenAI routing and structured compare leaves are
  both settled
