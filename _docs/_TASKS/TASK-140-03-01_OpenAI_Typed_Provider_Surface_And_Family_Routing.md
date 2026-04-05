# TASK-140-03-01: OpenAI Typed Provider Surface and Family Routing

**Parent:** [TASK-140-03](./TASK-140-03_OpenAI_Image_Input_Profiles_And_Structured_Compare_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Make the OpenAI family routing story explicit in config/runtime instead of
relying on a vague "generic external" assumption for all OpenAI-backed
compare-capable models.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `.env.example`

## Acceptance Criteria

- OpenAI family routing is documented and deterministic
- the repo records whether OpenAI should stay under `generic` transport naming
  or gain a first-class provider alias for clarity
- family-level routing remains compatible with the `TASK-139` override model

## Docs To Update

- `.env.example`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
