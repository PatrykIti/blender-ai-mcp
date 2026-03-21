# TASK-084-02: Search Transform and Pinned Entry Surface

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Enable search-first discovery as the default model for the `llm-guided` surface and define the pinned entry tools that remain directly visible.

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
  - enable the search transform for the `llm-guided` surface
- `server/adapters/mcp/surfaces.py`
  - declare the pinned entry tools list

---

## Initial Pinned Set

- `router_set_goal`
- `router_get_status`
- `workflow_catalog`
- prompt bridge tools from TASK-090 when they exist

`search_tools` and `call_tool` should come from the search transform itself and must not be duplicated manually.

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

## Acceptance Criteria

- `list_tools` on the `llm-guided` surface no longer returns the full tool catalog
- pinned tools stay visible and are not duplicated in search results

---

## Atomic Work Items

1. Enable built-in BM25 search on the `llm-guided` profile.
2. Keep the visible entry set intentionally tiny.
3. Validate that pinned tools do not reappear in search results.
4. Add explicit tests for search result usefulness on mega tools such as `scene_inspect` and `mesh_inspect`.
