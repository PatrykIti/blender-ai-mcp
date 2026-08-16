# TASK-150-05: Regression Pack And Docs For Server-Driven Guided Flows

**Parent:** [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md)
**Depends On:** [TASK-150-03](./TASK-150-03_Step_Gated_Visibility_And_Execution_Policy.md), [TASK-150-04](./TASK-150-04_Prompt_Bundle_Delivery_And_Flow_Aligned_Recommendations.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Protect the server-driven guided flow model with regression tests and clear
 operator-facing docs.

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`
- `tests/e2e/router/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- unit and E2E coverage prove the server, not just the prompt text, is shaping
  the intended guided flow
- docs explain the generic flow model and domain overlays clearly
- troubleshooting guidance distinguishes:
  - no-goal bootstrap
  - goal-active flow state
  - step-gated tool visibility
  - domain-specific overlays

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`
- `tests/e2e/router/`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-150-05-01](./TASK-150-05-01_Unit_And_Transport_Regression_Matrix_For_Flow_State_And_Gating.md) | Add unit and transport-backed regression coverage for flow state and step gating |
| 2 | [TASK-150-05-02](./TASK-150-05-02_Public_Docs_Troubleshooting_And_Changelog_Closeout.md) | Align README/MCP docs/troubleshooting and close the umbrella administratively |

## Completion Summary

- the regression/doc wave for TASK-150 is complete
- current docs and tests describe the shipped server-driven guided flow model,
  including execution enforcement
