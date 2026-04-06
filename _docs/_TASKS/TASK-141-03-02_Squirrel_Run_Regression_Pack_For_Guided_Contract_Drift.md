# TASK-141-03-02: Squirrel-Run Regression Pack for Guided Contract Drift

**Parent:** [TASK-141-03](./TASK-141-03_Inspect_Validate_Handoff_And_Regression_Pack.md)
**Depends On:** [TASK-141-03-01](./TASK-141-03-01_Inspect_Validate_Stop_And_Check_Operator_Story.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Protect the concrete squirrel-run contract-drift and `inspect_validate`
handoff shapes with focused automated coverage on the real guided surface path.

## Business Problem

The whole point of `TASK-141` is to stop rediscovering the same mistakes during
real guided creature runs. If the squirrel-run shapes are not captured as
surface-level regressions, the contract can drift back without any signal until
another real session fails.

This includes not only setup drift, but also the state where compare degrades,
truth remains available, and the operator still needs one explicit handoff into
inspect/measure/assert.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Acceptance Criteria

- focused tests cover the repeated squirrel-run failure shapes that motivated
  `TASK-141`
- docs regressions verify the canonical guided contract examples stay aligned
- loop regressions verify `inspect_validate` remains a true stop-and-check
  branch
- E2E/integration regressions verify the active surface keeps the same contract
  and handoff behavior seen in unit/docs expectations

## Leaf Work Items

- add targeted unit regressions for the selected compatibility and guidance
  policies
- add/refresh E2E/integration handoff coverage where the squirrel path depends
  on it
- ensure docs regressions protect the final operator story

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- update the parent summary so the shipped regression pack explicitly names the
  squirrel-run drift, compare-degradation, and handoff shapes it protects
