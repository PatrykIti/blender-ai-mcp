# TASK-090-03-01: Core Prompts as Tools Bridge

**Parent:** [TASK-090-03](./TASK-090-03_Prompts_As_Tools_Bridge.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-090-03](./TASK-090-03_Prompts_As_Tools_Bridge.md)  

---

## Objective

Implement the core code changes for **Prompts as Tools Bridge**.

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
