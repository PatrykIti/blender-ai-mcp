# TASK-095-01-01: Core Semantic Responsibility Policy and Code Audit

**Parent:** [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md)

---

## Objective

Implement the core code changes for **Semantic Responsibility Policy and Code Audit**.

---

## Repository Touchpoints

- `_docs/_ROUTER/semantic-boundary-audit.md`
- `server/router/application/classifier/intent_classifier.py`
- `server/router/application/classifier/workflow_intent_classifier.py`
- `server/router/application/resolver/parameter_resolver.py`
- `server/router/application/matcher/semantic_workflow_matcher.py`
- `server/router/application/matcher/ensemble_aggregator.py`
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
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
