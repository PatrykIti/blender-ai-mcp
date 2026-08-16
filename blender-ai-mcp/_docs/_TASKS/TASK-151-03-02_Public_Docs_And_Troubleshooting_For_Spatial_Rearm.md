# TASK-151-03-02: Public Docs And Troubleshooting For Spatial Re-Arm

**Parent:** [TASK-151-03](./TASK-151-03_Regression_And_Docs_For_Spatial_Rearm.md)
**Depends On:** [TASK-151-03-01](./TASK-151-03-01_Unit_And_Transport_Regression_Matrix_For_Spatial_Freshness.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Explain to operators and prompt authors that spatial checks are target-bound
and freshness-bound, not a one-time ritual at the beginning of the session.

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Planned Doc Topics

- why `scene_view_diagnostics(Camera)` does not satisfy a creature/building
  spatial gate
- when stale spatial state re-arms required checks
- how to read:
  - `active_target_scope`
  - `spatial_scope_fingerprint`
  - `spatial_state_version`
  - `spatial_state_stale`
  - `last_spatial_check_version`
  - `spatial_refresh_required`
  - `next_actions=["refresh_spatial_context"]`

## Planned File Work

- `README.md`
  - add one concise troubleshooting note on target-bound and freshness-bound
    spatial checks for guided sessions
- `_docs/_MCP_SERVER/README.md`
  - expand the `guided_flow_state` field table with the new spatial fields
  - document when build visibility/execution narrows back to spatial refresh
- `_docs/_PROMPTS/README.md`
  - explain that prompt authors should treat `refresh_spatial_context` as a
    real server-owned requirement, not advisory prose
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
  - assert the new wording/field names across README + MCP + prompt docs

## Acceptance Criteria

- docs clearly distinguish:
  - initial spatial gate
  - target-bound spatial validity
  - stale-spatial re-arm

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- create or update the parent TASK-151 changelog entry here

## Status / Closeout Note

- completed on 2026-04-09 after README, MCP docs, and prompt docs described
  the same field names and troubleshooting flow that transport tests expose

## Completion Summary

- public docs now explain target-bound scope binding, spatial freshness, and
  `refresh_spatial_context`
- docs parity tests now assert the new `guided_flow_state` fields and
  troubleshooting wording
