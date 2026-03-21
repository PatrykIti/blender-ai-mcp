# TASK-097-04: Inspection-Based Verification Integration

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md), [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)

---

## Objective

Verify important corrections through structured scene and mesh inspection instead of optimistic assumptions.

---

## Atomic Work Items

1. Map each high-risk correction family to the inspection contracts it depends on.
2. Execute verification after correction and before success is finalized.
3. Add tests for verified success, verification failure, and inconclusive verification.

---

## Acceptance Criteria

- high-risk verification depends on inspection-layer truth, not semantic guesswork
