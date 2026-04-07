# TASK-144-03: Goal-Aware Disclosure, Guided Adoption, And Regression Pack

**Parent:** [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)  
**Status:** ✅ Done  
**Priority:** 🟠 High  
**Depends On:** [TASK-144-01](./TASK-144-01_Projection_View_Space_Contract_And_Runtime_Foundation.md), [TASK-144-02](./TASK-144-02_Visibility_Report_Contract_And_Read_Surface.md)

**Completion Summary:** Completed on 2026-04-07. Landed the guided adoption
pack for TASK-144: `scene_view_diagnostics(...)` stays off the tiny bootstrap
surface, becomes available on build/inspect/handoff paths, and the reference
loop now uses only a compact recommendation surface (`view_diagnostics_hints`)
instead of embedding a heavyweight default view graph.

## Objective

Adopt the new view diagnostics into `llm-guided` in a way that is:

- goal-aware
- phase-aware
- on-demand
- payload-bounded

while keeping the default bootstrap surface small and keeping
`reference_compare_*` / `reference_iterate_*` free from heavyweight default
view-graph payloads.

## Current Runtime Baseline

The repo already has the two key seams this subtree should reuse:

- FastMCP surface shaping via `server/adapters/mcp/transforms/visibility_policy.py`
  and `server/adapters/mcp/guided_mode.py`
- bounded reference capture/compare orchestration in
  `server/adapters/mcp/areas/reference.py`

This means goal-aware disclosure is primarily a platform/discovery concern,
while on-demand guided adoption is a bounded reference-flow integration
concern.

## Implementation Direction

- keep FastMCP visibility/discovery as the owner of exposure policy
- let reference flows call or mention view diagnostics only when framing or
  occlusion ambiguity matters
- preserve the current staged compare/iterate payload discipline
- lock the intended behavior with docs and regression tests so the surface does
  not silently bloat later

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Acceptance Criteria

- new view diagnostics do not automatically appear on the tiny
  `llm-guided` bootstrap surface
- build/inspect or handoff states can expose or recommend the diagnostics when
  the active goal/phase justifies them
- `reference_compare_current_view(...)` and staged compare/iterate remain
  bounded by default; any adoption is opt-in or compact by design
- docs and regressions make the view-space-vs-truth-space boundary explicit

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md` when the execution branch is allowed to sync the
  board state

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-144-03-01](./TASK-144-03-01_LLM_Guided_Disclosure_And_Discovery_Shaping_For_View_Diagnostics.md) | Shape `llm-guided` visibility/discovery so the new diagnostics stay small, goal-aware, and phase-aware |
| 2 | [TASK-144-03-02](./TASK-144-03-02_On_Demand_Reference_Loop_Adoption_Docs_And_Regressions.md) | Teach bounded reference flows when to use the diagnostics and lock the boundary with docs/regressions |

## Status / Board Update

- closed on 2026-04-07 as part of the TASK-144 implementation wave
- the board is updated through the completed parent task
