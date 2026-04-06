# TASK-140-03-02: OpenAI Structured Compare Contract and Strict Output Policy

**Parent:** [TASK-140-03](./TASK-140-03_OpenAI_Image_Input_Profiles_And_Structured_Compare_Policy.md)
**Depends On:** [TASK-140-03-01](./TASK-140-03-01_OpenAI_Typed_Provider_Surface_And_Family_Routing.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Determine whether OpenAI families should keep using `generic_full` or whether
the repo needs one stricter OpenAI-specific compare contract for structured
checkpoint/reference flows.

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Acceptance Criteria

- the task records an explicit structured-output policy for OpenAI image-input
  families
- the repo knows whether smaller tiers such as mini/nano can safely reuse the
  same compare contract as larger tiers
- any newly introduced OpenAI-specific `vision_contract_profile` values remain
  typed in public `VisionAssistContract` surfaces and covered by regression
  tests
- prompt/schema/parser policy for OpenAI families is evidence-driven

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
