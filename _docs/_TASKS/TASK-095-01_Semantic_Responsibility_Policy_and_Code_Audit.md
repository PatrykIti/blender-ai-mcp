# TASK-095-01: Semantic Responsibility Policy and Code Audit

**Parent:** [TASK-095](./TASK-095_LaBSE_Semantic_Layer_Boundaries.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md)

---

## Objective

Audit current LaBSE usage across the repo and formalize the allowed responsibility boundary for the semantic layer.

---

## Planned Work

- create `_docs/_ROUTER/semantic-boundary-audit.md`
- classify current call sites across:
  - classifiers
  - matchers
  - parameter resolver and store
  - router adaptation

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-095-01-01](./TASK-095-01-01_Core_Semantic_Responsibility_Code_Audit.md) | Core Semantic Responsibility Policy and Code Audit | Core implementation layer |
| [TASK-095-01-02](./TASK-095-01-02_Tests_Semantic_Responsibility_Code_Audit.md) | Tests and Docs Semantic Responsibility Policy and Code Audit | Tests, docs, and QA |

---

## Acceptance Criteria

- the repo has a code-backed semantic boundary audit, not just a high-level architecture note
