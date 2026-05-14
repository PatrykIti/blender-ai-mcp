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

## Implementation Notes

- use this leaf to decide whether Qwen2.5-VL and Qwen3-VL can share one
  compare contract or need narrower behavior in prompting/backend/parsing
- keep the result grounded in explicit family ids and variant groupings
  instead of a generic “newer Qwen” bucket
- thread the resulting behavior back into the shared Qwen parent leaf so later
  docs/runtime owners stay aligned

## Runtime / Security Contract Notes

- do not let newer Qwen families inherit legacy behavior without evidence
- if Qwen3 variants diverge, keep the split explicit in diagnostics and docs

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`

## Status / Board Update

- remains nested under `TASK-140-01-03`
- should close before the parent Qwen behavior leaf is considered complete
