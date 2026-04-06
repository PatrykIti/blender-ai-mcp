# TASK-143-03: Goal-Aware Disclosure, Guided Adoption, and Regression Pack

**Parent:** [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md)
**Depends On:** [TASK-143-01](./TASK-143-01_Scope_Graph_Contract_And_Read_Only_Surface.md), [TASK-143-02](./TASK-143-02_Relation_Graph_Derivation_And_Truth_Layer_Convergence.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Expose the new scope/relation graph layer through goal-aware and phase-aware
guided disclosure, keep it on-demand, and lock the resulting product story
with regression/docs coverage.

## Business Problem

Even a well-designed graph layer can still regress the product if it is exposed
the wrong way:

- bootstrap-visible graph tools would reopen the large-catalog problem
- stage contracts could become heavier again if the graph is embedded by
  default
- router metadata could accidentally become the primary discovery/shaping
  mechanism even though FastMCP visibility/search should own that layer

This slice owns the surface discipline, not the graph math itself.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Acceptance Criteria

- the new graph artifacts are not bootstrap-visible by default on
  `llm-guided`
- there is one deterministic on-demand expansion story for when the current
  goal / phase / handoff needs richer spatial detail
- surface shaping remains owned primarily by FastMCP visibility/search rules,
  with router metadata used only as supporting retrieval context
- guided compare / iterate docs and prompts explain when to call the graph
  tools instead of trying to infer everything from dense stage payloads
- regression coverage protects both:
  - truth semantics
  - guided surface size / discoverability discipline

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-143-03-01](./TASK-143-03-01_Goal_Phase_Aware_Visibility_And_On_Demand_Expansion_Policy.md) | Define how the new graph artifacts stay off bootstrap while still being reachable through goal/phase-aware expansion |
| 2 | [TASK-143-03-02](./TASK-143-03-02_Regression_Docs_And_Prompt_Surface_Alignment.md) | Lock the disclosure story with public docs, prompt guidance, and regression coverage for surface size and discoverability |

## Status / Board Update

- keep board tracking on the parent `TASK-143`
- do not promote this slice independently unless disclosure/regression work is
  the only remaining TASK-143 branch
- this planning pass intentionally leaves `_docs/_TASKS/README.md` untouched
