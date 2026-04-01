# TASK-087-02-01: Core Router Parameter Resolution Integration

**Parent:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md)

---

## Objective

Implement the core code changes for **Router Parameter Resolution Integration**.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/router/application/resolver/parameter_resolver.py`

---

## Planned Work

- make `router_set_goal()` async-aware on the elicitation-capable `llm-guided` surface
- return typed unresolved bundles instead of only plain dict lists
- enforce request-bound elicitation lifecycle (no out-of-band prompting outside active MCP requests)
---

## Acceptance Criteria

- missing parameters can be collected without breaking the router goal flow
- workflow execution receives a consistent resolved payload
---

## Atomic Work Items

1. Add an async router entry tool for native elicitation.
2. Preserve the current second-call `resolved_params` fallback path.
3. Enforce request-bound elicitation semantics and reject out-of-band continuation attempts.
4. Validate that learned parameter storage still works after elicitation answers are applied.
