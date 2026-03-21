# TASK-086-04-01: Core Compatibility Adapters and Dispatcher Alignment

**Parent:** [TASK-086-04](./TASK-086-04_Compatibility_Adapters_and_Dispatcher_Alignment.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Implement the core code changes for **Compatibility Adapters and Dispatcher Alignment**.

---

## Repository Touchpoints

- `server/adapters/mcp/dispatcher.py`
- `server/adapters/mcp/router_helper.py`
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
