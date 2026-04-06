# TASK-128-01-03-03: Guided Handoff Payload, Visibility, and Regression

**Parent:** [TASK-128-01-03](./TASK-128-01-03_Creature_Aware_Guided_Handoff_And_Tool_Recipes.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Translate the creature recipe decisions into explicit guided handoff payloads,
visibility behavior, and regression coverage.

This is the leaf that closes the concrete audit finding that today’s
`guided_manual_build` payload is macro-first while the effective build session
still falls back to the broad generic `BUILD` surface.

## Current Drift To Resolve

Today the task package says "creature-aware guided handoff", but runtime
regressions still mostly protect a broad generic build payload. This leaf is
where the recipe becomes enforceable behavior.

More specifically, the current task package does not yet pin down:

- where the creature recipe becomes typed runtime state
- whether visibility/search shaping is global per phase or session-aware per
  handoff
- how to keep the generic `BUILD` benchmark while also adding one narrower
  creature-handoff benchmark

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Acceptance Criteria

- guided handoff payloads expose the creature-oriented direct/supporting tools
- visibility behavior remains deterministic, but the task makes the technical
  split explicit:
  - generic `BUILD` phase posture stays measurable on its own
  - creature-specific narrowing happens through the active guided handoff /
    session path instead of hand-wavy global phase shrinkage
- creature-session search behavior follows the same shaped tool set as the
  active creature handoff instead of silently searching the broad generic
  `BUILD` inventory
- regressions protect the intended creature handoff from future surface drift

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
