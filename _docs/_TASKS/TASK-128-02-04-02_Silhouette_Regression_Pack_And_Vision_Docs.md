# TASK-128-02-04-02: Silhouette Regression Pack and Vision Docs

**Parent:** [TASK-128-02-04](./TASK-128-02-04_Iterate_Stage_Integration_Docs_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add the documentation and regression-pack plan needed to keep the new
silhouette-analysis outputs stable.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Acceptance Criteria

- the repo has a focused regression plan for silhouette metrics/action hints
- vision docs explain the new deterministic perception layer
- test docs call out what should be covered at unit vs E2E level

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/`

## Changelog Impact

- include in the parent slice changelog entry when shipped
