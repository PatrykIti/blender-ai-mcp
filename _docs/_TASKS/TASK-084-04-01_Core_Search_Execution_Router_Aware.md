# TASK-084-04-01: Core Search Execution and Router-Aware Call Path

**Parent:** [TASK-084-04](./TASK-084-04_Search_Execution_and_Router_Aware_Call_Path.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Implement the core code changes for **Search Execution and Router-Aware Call Path**.

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/adapters/mcp_integration.py`
- `server/router/application/router.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
