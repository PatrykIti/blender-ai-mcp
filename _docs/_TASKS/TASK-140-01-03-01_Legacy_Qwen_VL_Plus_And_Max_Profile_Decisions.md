# TASK-140-01-03-01: Legacy Qwen-VL Plus and Max Profile Decisions

**Parent:** [TASK-140-01-03](./TASK-140-01-03_Qwen_Compare_Document_And_Exclusion_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Define the exact profile behavior for legacy `qwen-vl-plus` and
`qwen-vl-max`, including whether they stay on a generic compare contract, need
their own stricter compare profile, or should be treated as unstable-only
operator candidates.

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- legacy `qwen-vl-plus` and `qwen-vl-max` have an explicit product decision
- the repo does not imply that legacy Qwen compare behavior is equivalent to
  newer Qwen2.5-VL / Qwen3-VL lines without evidence
- operator-note instability and actual profile support are documented
  separately

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
