# TASK-084-04: Search Execution and Router-Aware Call Path

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Ensure that tools discovered through search execute through the same router and dispatcher policy path as directly listed tools.

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/adapters/mcp_integration.py`
- `server/router/application/router.py`

---

## Planned Work

- define the canonical call path for:
  - direct public tool calls
  - search proxy execution
  - router-emitted internal tool calls
- create `server/adapters/mcp/discovery/call_proxy.py`
- add parity tests for direct call vs discovered-call behavior

---

## Pseudocode

```python
def execute_discovered_tool(name, params, ctx):
    tool = provider.get_tool(name)
    assert tool is not None
    return tool(**params)
```

---

## Acceptance Criteria

- search discovery does not bypass router safety policy
- discovered-call execution remains behaviorally equivalent to direct calls
