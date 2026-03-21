# TASK-096-02: Confidence Scoring Normalization Across Engines

**Parent:** [TASK-096](./TASK-096_Confidence_Policy_for_Auto_Correction.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-096-01](./TASK-096-01_Correction_Taxonomy_and_Risk_Matrix.md)

---

## Objective

Normalize confidence signals from different engines into one shared confidence envelope.

---

## Repository Touchpoints

- `server/router/application/matcher/semantic_workflow_matcher.py`
- `server/router/application/matcher/ensemble_aggregator.py`
- `server/router/application/engines/tool_override_engine.py`
- `server/router/application/engines/error_firewall.py`

---

## Acceptance Criteria

- the policy engine receives one consistent confidence model
