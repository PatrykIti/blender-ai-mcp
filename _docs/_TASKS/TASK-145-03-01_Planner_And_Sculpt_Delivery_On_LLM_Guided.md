# TASK-145-03-01: Planner and Sculpt Delivery On `llm-guided`

**Parent:** [TASK-145-03](./TASK-145-03_Guided_Adoption_Visibility_Docs_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-03](./TASK-145-01-03_Planner_Summary_Placement_And_Compare_Iterate_Budget_Gates.md), [TASK-145-02-03](./TASK-145-02-03_Bounded_Sculpt_Metadata_And_Recommendation_Policy.md)

## Objective

Define the public-surface delivery model for planner and sculpt-context
artifacts on `llm-guided` so they stay:

- bounded
- discoverable when justified
- hidden when they would bloat bootstrap or generic build paths

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Acceptance Criteria

- no broad new planner/sculpt family becomes bootstrap-visible by default
- any planner or sculpt-context delivery path stays phase-aware and
  goal-aware
- search / visibility policy can surface the right bounded artifact when the
  current handoff justifies it
- default build and inspect phase footprints remain materially below the broad
  legacy catalog

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board change in this planning-only branch
