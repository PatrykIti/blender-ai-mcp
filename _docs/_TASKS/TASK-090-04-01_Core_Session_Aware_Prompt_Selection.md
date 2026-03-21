# TASK-090-04-01: Core Session-Aware Prompt Selection

**Parent:** [TASK-090-04](./TASK-090-04_Session_Aware_Prompt_Selection.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-090-04](./TASK-090-04_Session_Aware_Prompt_Selection.md)  

---

## Objective

Implement the core code changes for **Session-Aware Prompt Selection**.

---

## Repository Touchpoints

- Use the parent task touchpoints as the maximum write scope for this leaf; keep the implementation focused on the smallest core slice that lands the parent design.

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
