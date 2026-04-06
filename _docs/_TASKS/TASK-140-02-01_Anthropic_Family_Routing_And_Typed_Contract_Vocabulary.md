# TASK-140-02-01: Anthropic Family Routing and Typed Contract Vocabulary

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Family_Contracts_On_The_Existing_Provider_Surface.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add the model-id/family-routing and typed contract vocabulary needed to
resolve Claude-specific `vision_contract_profile` values on the existing
provider surface, without introducing a dedicated Anthropic provider by
default.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `.env.example`

## Acceptance Criteria

- Anthropic / Claude family-routing vocabulary is explicit
- typed runtime config and public `VisionAssistContract` result contracts can
  expose any Claude-specific `vision_contract_profile` cleanly
- config precedence remains deterministic and compatible with `TASK-139`
- unknown or non-matching Claude-family ids still fall back to `generic_full`
- this slice does not require a first-class Anthropic provider alias unless
  the current provider surface is proven insufficient

## Docs To Update

- `.env.example`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
