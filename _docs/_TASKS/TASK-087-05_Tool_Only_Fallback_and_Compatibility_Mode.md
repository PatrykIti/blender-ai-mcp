# TASK-087-05: Tool-Only Fallback and Compatibility Mode

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md)

---

## Objective

Preserve a clean fallback contract for clients that do not support the elicitation protocol.

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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-087-05-01](./TASK-087-05-01_Core_Fallback_Compatibility.md) | Core Tool-Only Fallback and Compatibility Mode | Core implementation layer |
| [TASK-087-05-02](./TASK-087-05-02_Tests_Fallback_Compatibility.md) | Tests and Docs Tool-Only Fallback and Compatibility Mode | Tests, docs, and QA |

---

## Acceptance Criteria

- no existing tool-only client loses capability after elicitation support is added

---

## Atomic Work Items

1. Define one stable fallback schema shared by router and workflow import flows.
2. Preserve current `resolved_params` continuation semantics.
3. Add compatibility tests against the current sync MCP adapter behavior.
