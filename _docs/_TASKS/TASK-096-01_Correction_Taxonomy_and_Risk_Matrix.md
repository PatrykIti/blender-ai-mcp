# TASK-096-01: Correction Taxonomy and Risk Matrix

**Parent:** [TASK-096](./TASK-096_Confidence_Policy_for_Auto_Correction.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md)

---

## Objective

Classify correction types and assign risk or blast-radius levels to each class.

---

## Planned Work

- create:
  - `server/router/domain/entities/correction_policy.py`
  - `_docs/_ROUTER/correction-risk-matrix.md`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-096-01-01](./TASK-096-01-01_Core_Correction_Taxonomy_Risk_Matrix.md) | Core Correction Taxonomy and Risk Matrix | Core implementation layer |
| [TASK-096-01-02](./TASK-096-01-02_Tests_Correction_Taxonomy_Risk_Matrix.md) | Tests and Docs Correction Taxonomy and Risk Matrix | Tests, docs, and QA |

---

## Acceptance Criteria

- every correction type has a clear classification and blast-radius label
