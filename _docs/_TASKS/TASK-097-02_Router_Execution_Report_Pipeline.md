# TASK-097-02: Router Execution Report Pipeline

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)

---

## Objective

Extend router output and `route_tool_call()` so multi-step execution produces a structured execution report instead of only a concatenated text response.

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`
- `server/router/infrastructure/logger.py`

---

## Acceptance Criteria

- multi-step execution is represented as structured data as well as optional summary text
