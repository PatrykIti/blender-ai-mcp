# TASK-143-03-01: Goal/Phase-Aware Visibility and On-Demand Expansion Policy

**Parent:** [TASK-143-03](./TASK-143-03_Goal_Aware_Disclosure_Guided_Adoption_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define how `llm-guided` exposes the new spatial graph artifacts only when the
current goal, phase, or guided handoff genuinely needs them.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- scope/relation graph tools are not part of the default bootstrap visible
  guided set
- one deterministic expansion path exists for relevant build/inspect flows
- expansion rules are goal-aware / phase-aware rather than history-scraping or
  fuzzy prompt guessing
- discovery/search can still surface the tools when appropriate without making
  them pinned defaults
- metadata supports retrieval, but FastMCP visibility/search remains the
  primary exposure mechanism

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-143`
- no `_docs/_TASKS/README.md` change in this planning pass
