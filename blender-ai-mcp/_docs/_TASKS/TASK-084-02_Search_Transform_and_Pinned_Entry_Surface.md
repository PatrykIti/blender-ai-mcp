# TASK-084-02: Search Transform and Pinned Entry Surface

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md), [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md), [TASK-091-03](./TASK-091-03_Version_Filtered_Server_Composition.md)

---

## Objective

Enable search-first discovery as the default model for the stabilized public `llm-guided` surface and define the pinned entry tools that remain directly visible.

## Completion Summary

This slice is now closed.

- `llm-guided` now defaults to search-first discovery
- pinned entry tools are exposed directly while the broader catalog is discovered on demand
- the rollout now runs on the shaped/versioned public surface rather than the raw internal catalog

---

## Repository Touchpoints

- future `server/adapters/mcp/transforms/discovery.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `README.md`

---

## Planned Work

### New Files To Create

- `server/adapters/mcp/discovery/search_surface.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

### Existing Files To Update

- `server/adapters/mcp/factory.py`
  - enable the search transform for the shaped public `llm-guided` surface after aliasing/version filters
- `server/adapters/mcp/surfaces.py`
  - declare the pinned entry tools list

---

## Initial Pinned Set

- `router_set_goal`
- `router_get_status`
- `workflow_catalog`
- prompt bridge tools from TASK-090 when they exist

`search_tools` and `call_tool` should come from the search transform itself and must not be duplicated manually.

### Rollout Rule

This subtask owns the public default rollout, not the earlier discovery plumbing.
It should index the post-transform public surface from TASK-086 / TASK-091 rather than the raw internal tool names currently mounted through direct `@mcp.tool()` wrappers.

---

## Pseudocode

```python
search_transform = BM25SearchTransform(
    always_visible=[
        "router_set_goal",
        "router_get_status",
        "workflow_catalog",
    ]
)
```

### Search Strategy

For this repo, prefer `BM25SearchTransform` on LLM-guided surfaces.
Keep regex search only as an internal-debug option when deterministic pattern matching is useful for diagnostics.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-084-02-01](./TASK-084-02-01_Core_Search_Transform_Pinned_Entry.md) | Core Search Transform and Pinned Entry Surface | Core implementation layer |
| [TASK-084-02-02](./TASK-084-02-02_Tests_Search_Transform_Pinned_Entry.md) | Tests and Docs Search Transform and Pinned Entry Surface | Tests, docs, and QA |

---

## Acceptance Criteria

- `list_tools` on the `llm-guided` surface no longer returns the full tool catalog
- search indexes the shaped public surface, not the pre-alias internal registration surface
- pinned tools stay visible and are not duplicated in search results

---

## Atomic Work Items

1. Enable built-in BM25 search on the shaped public `llm-guided` profile after aliasing/version filters are in place.
2. Keep the visible entry set intentionally tiny.
3. Validate that pinned tools do not reappear in search results.
4. Add explicit tests proving search operates on public names/aliases rather than raw internal registration names.
5. Add explicit tests for search result usefulness on mega tools such as `scene_inspect` and `mesh_inspect`.
