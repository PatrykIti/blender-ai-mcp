# TASK-155-02-01: Empty-Scene Bootstrap Primary Workset Path

**Parent:** [TASK-155-02](./TASK-155-02_Governor_Workset_Refresh_And_Bootstrap_Discipline.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make the guided flow distinguish an empty scene from a scene with a meaningful
target/workset, so spatial checks are not required before anything real exists
to inspect.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/scene.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`

## Acceptance Criteria

- after `scene_clean_scene(...)` leaves no meaningful objects, the guided
  state exposes a bootstrap-primary-workset next action instead of forcing a
  fake `Cube` / `Collection` spatial target
- once a primary mass/workset exists, target-bound spatial checks resume
- helper-only objects such as cameras/lights still do not satisfy creature or
  building spatial context
- docs and prompts explain the empty-scene branch explicitly

## Tests To Add/Update

- Unit:
  - add empty-scene state cases in
    `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - add visibility/search expectations in
    `tests/unit/adapters/mcp/test_visibility_policy.py` and
    `tests/unit/adapters/mcp/test_search_surface.py`
  - update docs parity in `tests/unit/adapters/mcp/test_public_surface_docs.py`
- E2E:
  - extend `tests/e2e/integration/test_guided_surface_contract_parity.py`
    for clean-scene -> primary mass bootstrap -> spatial checks

## Changelog Impact

- include in the TASK-155 changelog entry

## Completion Summary

- added `bootstrap_primary_workset` flow handling for guided sessions with no
  meaningful scene targets before spatial checks can be satisfied
