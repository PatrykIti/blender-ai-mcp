# TASK-140-03-01: OpenAI Family Routing and Typed Contract Vocabulary

**Parent:** [TASK-140-03](./TASK-140-03_OpenAI_Image_Input_Profiles_And_Structured_Compare_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Make the OpenAI family routing story explicit in config/runtime instead of
relying on a vague "generic external" assumption for all OpenAI-family model
ids on the existing external runtime path.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `.env.example`

## Acceptance Criteria

- OpenAI family routing is documented and deterministic
- the repo records whether OpenAI families can stay on the current external
  transport path while still gaining distinct contract profiles
- family-level routing remains compatible with the `TASK-139` override model
- unknown or non-matching OpenAI-family ids still fall back to `generic_full`
- any newly introduced OpenAI-specific `vision_contract_profile` values remain
  typed in public `VisionAssistContract` result surfaces

## Docs To Update

- `.env.example`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
