# TASK-128-01-03-03: Guided Handoff Payload, Visibility, and Regression

**Parent:** [TASK-128-01-03](./TASK-128-01-03_Creature_Aware_Guided_Handoff_And_Tool_Recipes.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Translate the creature recipe decisions into explicit guided handoff payloads,
visibility behavior, and regression coverage.

## Current Drift To Resolve

Today the task package says "creature-aware guided handoff", but runtime
regressions still mostly protect a broad generic build payload. This leaf is
where the recipe becomes enforceable behavior.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Acceptance Criteria

- guided handoff payloads expose the creature-oriented direct/supporting tools
- visibility behavior remains deterministic by phase/profile while protecting a
  narrower creature build baseline than the current generic `BUILD` footprint
- regressions protect the intended creature handoff from future surface drift

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
