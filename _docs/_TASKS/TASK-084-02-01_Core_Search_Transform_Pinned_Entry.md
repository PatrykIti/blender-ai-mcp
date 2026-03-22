# TASK-084-02-01: Core Search Transform and Pinned Entry Surface

**Parent:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Implement the core code changes for **Search Transform and Pinned Entry Surface**.

## Current State

The preview search surface is implemented in code:

- search-enabled surfaces can materialize `search_tools` and `call_tool`
- pinned entry tools are resolved on the shaped public surface
- search now operates on enriched public documents rather than raw internal tool names

This slice remains open because it is not yet the default public `llm-guided` rollout.

---

## Repository Touchpoints

- future `server/adapters/mcp/transforms/discovery.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/workflow_catalog.py`

---

## Planned Work

### New Files To Create

- `server/adapters/mcp/discovery/search_surface.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

### Existing Files To Update

- `server/adapters/mcp/factory.py`
  - enable the search transform for the `llm-guided` surface
- `server/adapters/mcp/surfaces.py`
  - declare the pinned entry tools list
---

## Acceptance Criteria

- `list_tools` on the `llm-guided` surface no longer returns the full tool catalog
- pinned tools stay visible and are not duplicated in search results
---

## Atomic Work Items

1. Enable built-in BM25 search on the `llm-guided` profile.
2. Keep the visible entry set intentionally tiny.
3. Validate that pinned tools do not reappear in search results.
4. Add explicit tests for search result usefulness on mega tools such as `scene_inspect` and `mesh_inspect`.
