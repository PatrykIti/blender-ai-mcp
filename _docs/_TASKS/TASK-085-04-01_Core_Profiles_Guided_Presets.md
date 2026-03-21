# TASK-085-04-01: Core Client Profiles and Guided Mode Presets

**Parent:** [TASK-085-04](./TASK-085-04_Client_Profiles_and_Guided_Mode_Presets.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-04](./TASK-085-04_Client_Profiles_and_Guided_Mode_Presets.md)  

---

## Objective

Implement the core code changes for **Client Profiles and Guided Mode Presets**.

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
