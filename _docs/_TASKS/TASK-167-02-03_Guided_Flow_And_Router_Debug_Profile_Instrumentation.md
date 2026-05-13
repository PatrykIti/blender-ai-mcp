# TASK-167-02-03: Guided Flow And Router Debug Profile Instrumentation

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-02](./TASK-167-02_Runtime_Instrumentation_And_Targeted_Log_Routing.md)
**Objective:** Own the combined `guided_flow` / `router` branch only as a decomposition parent, then split the actual implementation into two focused leaves so guided-flow state shaping and router/runtime summaries do not get implemented in one oversized pass.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/areas/router.py`, `server/router/application/router.py`, `server/router/application/matcher/ensemble_matcher.py`, `server/router/infrastructure/logger.py`, `server/adapters/mcp/router_helper.py`, `server/application/tool_handlers/router_handler.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/router/application/test_router_handler_parameters.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/router/infrastructure/test_logger.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`
**Acceptance Criteria:**
- the guided-flow/runtime behavior is isolated in its own implementation leaf
- the router/logger/audit behavior is isolated in its own implementation leaf
- this parent cannot close before both children are implemented and validated on their owned seams

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-167-02-03-01](./TASK-167-02-03-01_Guided_Flow_Debug_Profile_Instrumentation.md) | Instrument guided-flow step transitions, refresh barriers, and state-shaping seams |
| 2 | [TASK-167-02-03-02](./TASK-167-02-03-02_Router_Debug_Profile_Instrumentation.md) | Instrument router goal/status/logger/audit seams |

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this parent owns the split |
|------|--------------------|---------------------|--------------------------------|
| `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py` | guided-flow state shaping and persistence | current guided-flow seams | this half belongs in the guided-flow child leaf |
| `server/adapters/mcp/areas/router.py`, `server/router/application/router.py`, `server/router/application/matcher/ensemble_matcher.py`, `server/router/infrastructure/logger.py`, `server/adapters/mcp/router_helper.py`, `server/application/tool_handlers/router_handler.py` | router goal/status/logger/audit seams | current router seams | this half belongs in the router child leaf |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | guided-flow owner lane | current guided-flow tests | proof for the first child |
| `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/router/application/test_router_handler_parameters.py`, `tests/unit/router/infrastructure/test_logger.py` | router owner lanes | current router/logger tests | proof for the second child |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | shared integration proof lane | current refresh-barrier and router-status transport surface | integration proof shared by both children where needed |

## Implementation Notes

- keep this parent as decomposition-only coordination, not as the place where
  both runtime branches are implemented together
- guided-flow and router share adjacent seams, but they are different execution
  tracks and should be proved separately

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167-02`
- should close only after `TASK-167-02-03-01` and `TASK-167-02-03-02` are
  implemented and validated

## Validation Commands

- `git diff --check`
- the parent should close only after the focused owner lanes in the two child
  leaves are green

## Validation Category

- docs/decomposition sanity only in this parent
- `git diff --check`
