# TASK-083-03-01: Core Server Factory and Composition Root

**Parent:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Implement the core code changes for **Server Factory and Composition Root**.

---

## Repository Touchpoints

- `server/adapters/mcp/instance.py`
- `server/adapters/mcp/server.py`
- `server/main.py`
- `server/infrastructure/config.py`
- `server/infrastructure/di.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-083-03-01-01](./TASK-083-03-01-01_Surface_Profile_Settings_and_Config.md) | Surface Profile Settings and Config | Core slice |
| [TASK-083-03-01-02](./TASK-083-03-01-02_Server_Factory_and_Bootstrap_Path.md) | Server Factory and Bootstrap Path | Core slice |

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
