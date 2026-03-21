# TASK-084-02: Search Transform and Pinned Entry Surface

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Enable search-first discovery as the default model for LLM-first surfaces and define the pinned entry tools that remain directly visible.

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
  - enable the search transform for LLM-first surfaces
- `server/adapters/mcp/surfaces.py`
  - declare the pinned entry tools list

---

## Initial Pinned Set

- `router_set_goal`
- `router_get_status`
- `workflow_catalog`
- `search_tools`
- `call_tool`
- prompt bridge tools from TASK-090 when they exist

---

## Pseudocode

```python
search_transform = RegexSearchTransform(
    always_visible=[
        "router_set_goal",
        "router_get_status",
        "workflow_catalog",
    ]
)
```

---

## Acceptance Criteria

- `list_tools` on the LLM-first surface no longer returns the full tool catalog
- pinned tools stay visible and are not duplicated in search results
