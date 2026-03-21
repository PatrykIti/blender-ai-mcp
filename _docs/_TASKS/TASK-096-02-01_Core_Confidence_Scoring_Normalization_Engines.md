# TASK-096-02-01: Core Confidence Scoring Normalization Across Engines

**Parent:** [TASK-096-02](./TASK-096-02_Confidence_Scoring_Normalization_Across_Engines.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-096-01](./TASK-096-01_Correction_Taxonomy_and_Risk_Matrix.md)

---

## Objective

Implement the core code changes for **Confidence Scoring Normalization Across Engines**.

---

## Repository Touchpoints

- `server/router/application/matcher/semantic_workflow_matcher.py`
- `server/router/application/matcher/ensemble_aggregator.py`
- `server/router/application/engines/tool_override_engine.py`
- `server/router/application/engines/error_firewall.py`

---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- the policy engine receives one consistent confidence model
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
