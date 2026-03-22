# TASK-096-02: Confidence Scoring Normalization Across Engines

**Parent:** [TASK-096](./TASK-096_Confidence_Policy_for_Auto_Correction.md)  
**Status:** 🚧 In Progress  
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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-096-02-01](./TASK-096-02-01_Core_Confidence_Scoring_Normalization_Engines.md) | Core Confidence Scoring Normalization Across Engines | Core implementation layer |
| [TASK-096-02-02](./TASK-096-02-02_Tests_Confidence_Scoring_Normalization_Engines.md) | Tests and Docs Confidence Scoring Normalization Across Engines | Tests, docs, and QA |

---

## Acceptance Criteria

- the policy engine receives one consistent confidence model
