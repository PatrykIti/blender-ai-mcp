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

### Slice Outputs

- normalize confidence/policy context into deterministic decision inputs
- route medium-confidence and session-memory behavior through explicit policy semantics
- expose operator-visible policy context without ambiguity

### Implementation Checklist

- touch `server/router/application/matcher/semantic_workflow_matcher.py` with explicit change notes and boundary rationale
- touch `server/router/application/matcher/ensemble_aggregator.py` with explicit change notes and boundary rationale
- touch `server/router/application/engines/tool_override_engine.py` with explicit change notes and boundary rationale
- touch `server/router/application/engines/error_firewall.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- policy decisions are deterministic for equivalent inputs
- session/operator context is consistent with executed decisions
- escalation behavior is test-covered and contract-driven
- slice integrates with audit/reporting layers without hidden heuristics

---

## Atomic Work Items

1. Implement confidence/session/policy behavior in listed touchpoints.
2. Add tests for deterministic decisions, escalation, and session persistence/reset.
3. Capture policy decision traces for representative risk classes.
4. Document operator-facing policy semantics and fields.
