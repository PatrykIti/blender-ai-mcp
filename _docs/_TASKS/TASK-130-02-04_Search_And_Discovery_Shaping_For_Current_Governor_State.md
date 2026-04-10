# TASK-130-02-04: Search And Discovery Shaping For Current Governor State

**Parent:** [TASK-130-02](./TASK-130-02_Generic_Guided_Governor_Hardening_For_Step_Target_And_Domain_Discipline.md)
**Depends On:** [TASK-130-02-03](./TASK-130-02-03_Domain_Adaptive_Progression_And_Inspect_Escalation.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Shape guided search/discovery around the current governor state so results are
smaller, less noisy, and more aligned with the current step/domain/workset.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Detailed Implementation Notes

- reuse current search-first surface and visibility shaping
- avoid broad search result floods when the governor already knows the current
  bounded work area
- prefer narrowing by:
  - current step
  - allowed families/roles
  - active target/workset
  - recovery/inspect phase semantics

## Planned Unit Test Scenarios

- current-step searches return bounded result sets
- search/list/status tell one coherent governor story
- the model no longer needs broad exploratory search to reach the obvious next
  move in common guided sessions

## Changelog Impact

- include in the parent TASK-130 changelog entry

## Completion Summary

- exact tool-name searches now return a tighter, smaller result row and no
  longer need to dump the full expanded tool definition payload
