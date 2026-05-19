# TASK-169-01: Guided Manual Build Entry And Multi-Reference Stabilization

**Parent:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Status:** ✅ Done
**Completed:** 2026-05-19
**Priority:** 🔴 High
**Objective:** Stabilize the no-match creature handoff plus same-session multi-reference understanding refresh so early creature build decisions do not rely on a stale one-reference state.
**Repository Touchpoints:** `server/application/tool_handlers/router_handler.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/router/test_guided_manual_handoff.py`
**Acceptance Criteria:**
- a creature `guided_manual_build` run can preserve explicit reference-guided intent without starting from a stale partial-RU state
- same-session front+side reference attach sequences cannot leave the controller acting on an older one-reference understanding when two active references are already expected
- readiness/feedback surfaces stay typed and reuse the current session/router/reference seams instead of introducing a second orchestration flow

## Implementation Notes

- reuse the current no-match and reference-refresh owners:
  - `RouterToolHandler._looks_like_reference_guided_manual_build_goal(...)`
  - `RouterToolHandler._no_match_response(...)`
  - `_maybe_attach_guided_handoff(...)`
  - `build_guided_handoff_payload(...)`
  - `handle_reference_images(...)`
  - `refresh_reference_understanding_summary(...)`
  - guided readiness builders in `session_capabilities_bootstrap.py`
- the goal is not “force serial attach from the client”; the runtime should
  remain stable even when the client attaches references in quick succession
- keep the transport-safe session model:
  - one goal
  - one active reference store
  - one RU summary
  - one readiness projection
- if the runtime cannot yet trust the refreshed two-reference state, the
  guided feedback should tell the client to finish reference stabilization
  before continuing broad modeling

## Pseudocode

```python
if action == "attach":
    persist_reference(...)
    refreshed = await refresh_reference_understanding_summary(...)
    if refreshed.reference_images_changed_during_refresh:
        refreshed = await refresh_reference_understanding_summary(...)
    return project_reference_feedback(refreshed)
```

## Runtime / Security Contract Notes

- keep one session-owned RU summary authority; no parallel transient summary
  channel
- do not expose private temp-path or provider details in stabilization errors
- fail closed through readiness/feedback when the refreshed state is not yet the
  state the next build step should trust

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Docs To Update

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md` if readiness wording changes

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Completion Summary

- no-match creature handoff now preserves the guided manual-build reference
  context instead of dropping back to an unrelated workflow route
- same-session front+side reference attach flows refresh one shared
  reference-understanding summary and gate-id set instead of leaving the
  session on a stale one-reference state
- transport and unit coverage already pin the squirrel front/side readiness
  flow through the current `reference_images(...)`, router, and gate-state
  seams

## Status / Board Update

- closed with parent `TASK-169`; no standalone board row is needed

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/router/test_guided_manual_handoff.py -q`

## Validation Category

- session/router/reference stabilization proof
