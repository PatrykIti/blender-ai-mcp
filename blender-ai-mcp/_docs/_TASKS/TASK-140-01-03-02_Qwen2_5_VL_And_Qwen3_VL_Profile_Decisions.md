# TASK-140-01-03-02: Qwen2.5-VL and Qwen3-VL Profile Decisions

**Parent:** [TASK-140-01-03](./TASK-140-01-03_Qwen_Compare_Document_And_Exclusion_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the compare-contract behavior for Qwen2.5-VL and Qwen3-VL families,
including whether newer lines can share one profile or need distinct prompt /
schema / parser handling.

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- Qwen2.5-VL and Qwen3-VL product behavior is explicit instead of inherited by
  accident from legacy Qwen-VL handling
- the task records whether Qwen3-VL thinking/instruct/plus/flash variants can
  share one compare profile or need further separation
- structured compare support is documented per family rather than per vague
  "Qwen" label

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
