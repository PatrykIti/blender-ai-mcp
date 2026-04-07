# TASK-146-01: Workflow Trigger Boundaries And MCP Guardrail Coverage

**Parent:** [TASK-146](./TASK-146_Guided_Runtime_Guardrails_Vision_Profile_And_Prompting_Hardening.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

**Completion Summary:** Completed on 2026-04-07. Tightened the trigger
boundary so explicit no-match/manual goals suppress heuristic workflow
activation during ordinary direct tool usage, and expanded unit/E2E regression
coverage around the repaired guided MCP guardrails.

## Objective

Repair the trigger/guardrail layer so ordinary guided direct tool calls do not
unexpectedly activate unrelated workflows, and add materially stronger unit/E2E
coverage around the MCP/runtime logic that is supposed to prevent that class of
failure.

## Repository Touchpoints

- `server/router/application/triggerer/workflow_triggerer.py`
- `server/router/application/router.py`
- `server/router/adapters/mcp_integration.py`
- `server/adapters/mcp/areas/`
- `tests/unit/router/application/triggerer/`
- `tests/unit/router/adapters/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/router/`

## Acceptance Criteria

- direct tool calls such as ordinary `modeling_transform_object(...)` do not
  spuriously trigger unrelated workflows
- trigger decisions are bounded by clearer direct-call / workflow-intent rules
- unit tests cover the repaired trigger boundary rules
- E2E tests cover representative guided direct-call sequences that previously
  drifted into workflow activation

## Docs To Update

- `_docs/_TESTS/README.md`
- `_docs/_MCP_SERVER/README.md` if operator-visible behavior changes

## Tests To Add/Update

- `tests/unit/router/application/triggerer/`
- `tests/unit/router/adapters/test_mcp_integration.py`
- `tests/unit/adapters/mcp/`
- `tests/e2e/router/`

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-146-01-01](./TASK-146-01-01_Direct_Call_Workflow_Trigger_Suppression_Rules.md) | Tighten the direct-call vs workflow-trigger boundary itself |
| 2 | [TASK-146-01-02](./TASK-146-01-02_Unit_And_E2E_Regression_Pack_For_Shaped_MCP_Guardrails.md) | Lock the repaired behavior with stronger unit and E2E coverage |

## Status / Board Update

- closed on 2026-04-07 with TASK-146
