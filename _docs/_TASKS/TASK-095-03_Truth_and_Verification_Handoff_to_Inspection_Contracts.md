# TASK-095-03: Truth and Verification Handoff to Inspection Contracts

**Parent:** [TASK-095](./TASK-095_LaBSE_Semantic_Layer_Boundaries.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)

---

## Objective

Move truth and verification decisions onto structured inspection contracts instead of semantic confidence.

---

## Atomic Work Items

1. Identify every place where semantic confidence currently leaks into truth-like decisions.
2. Replace those decisions with explicit inspection contract checks.
3. Add tests proving scene truth no longer depends on semantic score alone.

---

## Acceptance Criteria

- semantic confidence is not used as a proxy for scene truth
