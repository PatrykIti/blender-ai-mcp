# TASK-087-02: Router Parameter Resolution Integration

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md)

---

## Objective

Integrate `router_set_goal` and `RouterToolHandler.set_goal()` with `ctx.elicit()` so missing workflow parameters can be collected through a server-driven interaction flow.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/router/application/resolver/parameter_resolver.py`

---

## Planned Work

- make `router_set_goal()` async-aware on the elicitation-capable surface
- return typed unresolved bundles instead of only plain dict lists

---

## Pseudocode

```python
result = await ctx.elicit(
    message="Missing workflow parameters",
    response_type=RouterParamAnswers,
)
```

---

## Acceptance Criteria

- missing parameters can be collected without breaking the router goal flow
- workflow execution receives a consistent resolved payload
