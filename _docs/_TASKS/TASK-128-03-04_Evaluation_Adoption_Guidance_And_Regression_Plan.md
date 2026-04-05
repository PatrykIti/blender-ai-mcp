# TASK-128-03-04: Evaluation, Adoption Guidance, and Regression Plan

**Parent:** [TASK-128-03](./TASK-128-03_Optional_Part_Segmentation_Sidecar_And_Part_Aware_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Define the cost/latency gates, operator guidance, and test strategy that must
exist before any part-segmentation sidecar becomes a serious supported option.

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`
- `tests/unit/adapters/mcp/test_vision_*`
- `tests/e2e/vision/`

## Acceptance Criteria

- the repo has explicit adoption/evaluation gates for the sidecar path
- docs explain when the heavier path is worth using
- a regression/test plan exists before rollout

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-03-04-01](./TASK-128-03-04-01_Evaluation_Matrix_Cost_Gates_And_Runtime_Verdict.md) | Define the evaluation matrix and cost/latency gates for the optional sidecar |
| 2 | [TASK-128-03-04-02](./TASK-128-03-04-02_Operator_Docs_And_Regression_Plan.md) | Define operator docs and the regression plan required before rollout |
