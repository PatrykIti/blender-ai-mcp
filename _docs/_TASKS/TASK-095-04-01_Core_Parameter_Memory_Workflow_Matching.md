# TASK-095-04-01: Core Parameter Memory and Workflow Matching Hardening

**Parent:** [TASK-095-04](./TASK-095-04_Parameter_Memory_and_Workflow_Matching_Hardening.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md)

---

## Objective

Implement the core code changes for **Parameter Memory and Workflow Matching Hardening**.

---

## Repository Touchpoints

- `server/router/application/resolver/parameter_resolver.py`
- `server/router/application/resolver/parameter_store.py`
- `server/router/application/matcher/semantic_workflow_matcher.py`
- `server/router/application/matcher/ensemble_aggregator.py`

---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- learned mapping reuse is clearly separated from execution-policy approval
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
