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

- make `router_set_goal()` async-aware on the elicitation-capable `llm-guided` surface
- return typed unresolved bundles instead of only plain dict lists

---

## Pseudocode

```python
result = await ctx.elicit(
    message="Missing workflow parameters",
    response_type=RouterParamAnswers,
)
```

### Compatibility Rule

Do not require every surface to use native elicitation.
This task should add:

- native elicitation on `llm-guided`
- fallback `needs_input` payloads on `legacy-flat`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-087-02-01](./TASK-087-02-01_Core_Router_Parameter_Resolution_Integration.md) | Core Router Parameter Resolution Integration | Core implementation layer |
| [TASK-087-02-02](./TASK-087-02-02_Tests_Router_Parameter_Resolution_Integration.md) | Tests and Docs Router Parameter Resolution Integration | Tests, docs, and QA |

---

## Acceptance Criteria

- missing parameters can be collected without breaking the router goal flow
- workflow execution receives a consistent resolved payload

---

## Atomic Work Items

1. Add an async router entry tool for native elicitation.
2. Preserve the current second-call `resolved_params` fallback path.
3. Validate that learned parameter storage still works after elicitation answers are applied.
