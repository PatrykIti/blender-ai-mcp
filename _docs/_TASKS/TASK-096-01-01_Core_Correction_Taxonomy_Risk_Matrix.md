# TASK-096-01-01: Core Correction Taxonomy and Risk Matrix

**Parent:** [TASK-096-01](./TASK-096-01_Correction_Taxonomy_and_Risk_Matrix.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md)

---

## Objective

Implement the core code changes for **Correction Taxonomy and Risk Matrix**.

---

## Repository Touchpoints

- `server/router/domain/entities/correction_policy.py`
- `_docs/_ROUTER/correction-risk-matrix.md`
- `tests/unit/router/application/test_correction_policy_engine.py`
---

## Planned Work

- create:
  - `server/router/domain/entities/correction_policy.py`
  - `_docs/_ROUTER/correction-risk-matrix.md`
---

## Acceptance Criteria

- every correction type has a clear classification and blast-radius label
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
