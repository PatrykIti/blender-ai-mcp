# TASK-086-01-01: Core Public Surface Manifest and Naming Conventions

**Parent:** [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md)  

---

## Objective

Implement the core code changes for **Public Surface Manifest and Naming Conventions**.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/dispatcher.py`

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
