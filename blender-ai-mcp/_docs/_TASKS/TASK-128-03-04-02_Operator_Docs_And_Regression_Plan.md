# TASK-128-03-04-02: Operator Docs and Regression Plan

**Parent:** [TASK-128-03-04](./TASK-128-03-04_Evaluation_Adoption_Guidance_And_Regression_Plan.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Define the operator guidance and regression coverage that should exist before
the sidecar path is presented as a serious supported option.

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`
- `tests/unit/adapters/mcp/test_vision_*`
- `tests/e2e/vision/`

## Acceptance Criteria

- docs explain the optional sidecar path clearly
- the regression plan covers both enabled and disabled/fallback paths
- the rollout expectations stay consistent with the repo's boundary model

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_*`
- `tests/e2e/vision/`

## Changelog Impact

- include in the parent slice changelog entry when shipped
