# TASK-087-05-01: Core Tool-Only Fallback and Compatibility Mode

**Parent:** [TASK-087-05](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md)

---

## Objective

Implement the core code changes for **Tool-Only Fallback and Compatibility Mode**.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/adapters/mcp/elicitation_contracts.py`
- `server/application/tool_handlers/router_handler.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
---

## Planned Work

- define fallback payload shape:
  - `status: "needs_input"`
  - typed `questions`
  - stable `request_id`
  - stable `question_set_id`
- let `router_set_goal` choose between:
  - native elicitation flow when supported
  - fallback payload when not supported
---

## Acceptance Criteria

- no existing tool-only client loses capability after elicitation support is added

---

## Atomic Work Items

1. Define one stable fallback schema shared by router and workflow import flows.
2. Preserve current `resolved_params` continuation semantics.
3. Add compatibility tests against the current sync MCP adapter behavior.
