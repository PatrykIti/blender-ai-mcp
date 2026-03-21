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
- let `router_set_goal` choose between:
  - native elicitation flow when supported
  - fallback payload when not supported

---

## Acceptance Criteria

- no existing tool-only client loses capability after elicitation support is added
