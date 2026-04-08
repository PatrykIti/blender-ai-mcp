# TASK-149-03: Regression Pack And Docs For Default Spatial Support

**Parent:** [TASK-149](./TASK-149_Guided_Default_Spatial_Graph_And_View_Diagnostics_For_All_Goal_Oriented_Sessions.md)
**Depends On:** [TASK-149-01](./TASK-149-01_Visibility_Policy_And_Guided_Handoff_Default_Spatial_Support.md), [TASK-149-02](./TASK-149-02_Prompt_And_Loop_Adoption_Of_Default_Spatial_Support.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Protect the new default spatial-support behavior with regression tests and
operator-facing docs.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- unit coverage proves that spatial graph/view helpers are visible after goal
  activation across the intended guided phases
- any transport-backed or session-backed regression needed for real
  handoff/list-tools parity is added
- docs no longer describe one thing while the real guided surface exposes
  another

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/` as needed

## Changelog Impact

- include in the parent umbrella changelog entry when shipped
