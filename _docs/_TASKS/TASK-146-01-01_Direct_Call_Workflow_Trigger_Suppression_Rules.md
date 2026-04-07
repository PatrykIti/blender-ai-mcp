# TASK-146-01-01: Direct-Call Workflow Trigger Suppression Rules

**Parent:** [TASK-146-01](./TASK-146-01_Workflow_Trigger_Boundaries_And_MCP_Guardrail_Coverage.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-146-01](./TASK-146-01_Workflow_Trigger_Boundaries_And_MCP_Guardrail_Coverage.md)

## Objective

Define and implement stricter rules for when workflow triggering is allowed to
activate during guided direct-call execution, so ordinary bounded tool usage
does not unexpectedly pivot into unrelated workflow logic.

## Repository Touchpoints

- `server/router/application/triggerer/workflow_triggerer.py`
- `server/router/application/router.py`
- related trigger/telemetry tests

## Acceptance Criteria

- direct calls with explicit tool intent do not trigger heuristic workflow
  activation without a stronger rule gate
- trigger behavior is deterministic and explainable in logs/tests
- regression tests cover representative false-positive cases

## Docs To Update

- `_docs/_TESTS/README.md` if validation scope changes

## Tests To Add/Update

- `tests/unit/router/application/triggerer/`
- `tests/unit/router/adapters/`

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Status / Board Update

- leaf for the direct-call trigger boundary repair
