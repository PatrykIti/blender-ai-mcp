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

## Acceptance Criteria

- the repo has a code-backed semantic boundary audit, not just a high-level architecture note
