# TASK-140-01-03-01: Legacy Qwen-VL Plus and Max Profile Decisions

**Parent:** [TASK-140-01-03](./TASK-140-01-03_Qwen_Compare_Document_And_Exclusion_Profiles.md)
**Status:** ⏭️ Superseded
**Priority:** 🟠 High
**Superseded By:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Superseded Reason:** Replaced by the capability-first OpenRouter metadata, fallback capability registry, and request-policy model. Family-specific profiles return under `TASK-187` only when harness/operator evidence shows a real contract delta.

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

## Implementation Notes

- keep this leaf limited to legacy `qwen-vl-plus` / `qwen-vl-max` behavior
  instead of collapsing it into the newer Qwen2.5/Qwen3 matrix
- use the existing prompting/parsing seams to decide whether legacy support is:
  - compare-capable
  - generic-only
  - unstable/operator-only
- record instability separately from true product support so later docs do not
  overclaim these legacy families

## Runtime / Security Contract Notes

- do not let legacy-family support become the default for newer Qwen lines
- if legacy models remain unstable, keep diagnostics explicit instead of
  treating them as normal compare defaults

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py -q`

## Status / Board Update

- remains nested under `TASK-140-01-03`
- should close before the parent Qwen behavior leaf is considered complete
