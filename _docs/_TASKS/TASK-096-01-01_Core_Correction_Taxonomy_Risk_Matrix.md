# TASK-096-01-01: Core Correction Taxonomy and Risk Matrix

**Parent:** [TASK-096-01](./TASK-096-01_Correction_Taxonomy_and_Risk_Matrix.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-096-01](./TASK-096-01_Correction_Taxonomy_and_Risk_Matrix.md)  

---

## Objective

Implement the core code changes for **Correction Taxonomy and Risk Matrix**.

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
