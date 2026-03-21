# TASK-083-02-01: Core Provider-Based Component Inventory

**Parent:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Implement the core code changes for **Provider-Based Component Inventory**.

---

## Repository Touchpoints

- `server/adapters/mcp/instance.py`
- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/areas/__init__.py`
- `server/infrastructure/di.py`
- `server/adapters/mcp/dispatcher.py`
- `server/application/tool_handlers/*.py`
- `server/domain/tools/*.py`

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
