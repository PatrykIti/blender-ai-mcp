# TASK-146-01-02: Unit And E2E Regression Pack For Shaped MCP Guardrails

**Parent:** [TASK-146-01](./TASK-146-01_Workflow_Trigger_Boundaries_And_MCP_Guardrail_Coverage.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-146-01-01](./TASK-146-01-01_Direct_Call_Workflow_Trigger_Suppression_Rules.md)

**Completion Summary:** Completed on 2026-04-07. Added focused regression
coverage for the repaired guided guardrails, including unit tests for the
triggerer boundary and E2E coverage for a real no-match/manual guided session
that should not reopen an unrelated workflow.

## Objective

Expand the regression suite around the MCP/runtime logic that governs shaped
surface behavior so real guided sessions are less likely to regress silently in
areas such as:

- hidden tool rejection
- phase-locked tool rejection
- direct-call validation drift
- workflow trigger boundaries
- search-first vs speculative direct-call behavior

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `tests/unit/router/adapters/`
- `tests/e2e/router/`
- `tests/e2e/tools/`

## Acceptance Criteria

- representative unit coverage exists for the repaired guardrail paths
- representative E2E coverage exists for shaped guided sessions that stay on
  direct tools/macros without accidental workflow activation
- docs reflect the new validation slices

## Docs To Update

- `_docs/_TESTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/`
- `tests/unit/router/adapters/`
- `tests/e2e/router/`

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Status / Board Update

- closed on 2026-04-07 with TASK-146
