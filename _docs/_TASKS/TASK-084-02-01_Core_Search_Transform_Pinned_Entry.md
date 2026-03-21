# TASK-084-02-01: Core Search Transform and Pinned Entry Surface

**Parent:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)  

---

## Objective

Implement the core code changes for **Search Transform and Pinned Entry Surface**.

---

## Repository Touchpoints

- `future `server/adapters/mcp/transforms/discovery.py``
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/workflow_catalog.py`

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
