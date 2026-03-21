# TASK-096-06-01: Core Policy Tests, Telemetry, and Documentation

**Parent:** [TASK-096-06](./TASK-096-06_Policy_Tests_Telemetry_and_Documentation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-096-04](./TASK-096-04_Medium_Confidence_Elicitation_and_Escalation.md), [TASK-096-05](./TASK-096-05_Session_Memory_and_Operator_Transparency.md)

---

## Objective

Implement the core code changes for **Policy Tests, Telemetry, and Documentation**.

---

## Repository Touchpoints

- `tests/unit/router/application/test_correction_policy_engine.py`
- `_docs/_ROUTER/correction-risk-matrix.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `README.md`
---

## Planned Work

### Deliverables

- implement the slice behavior end-to-end across: `tests/unit/router/application/test_correction_policy_engine.py`, `_docs/_ROUTER/correction-risk-matrix.md`, `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`, `README.md`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `tests/unit/router/application/test_correction_policy_engine.py` with an explicit change note (or explicit no-change rationale)
- touch `_docs/_ROUTER/correction-risk-matrix.md` with an explicit change note (or explicit no-change rationale)
- touch `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` with an explicit change note (or explicit no-change rationale)
- touch `README.md` with an explicit change note (or explicit no-change rationale)
- add or update focused regression coverage for the changed slice behavior
- capture one before/after example of the affected runtime surface (payload, config, or execution flow)

### Review Notes To Attach

- short rationale for every changed touchpoint
- explicit note of any deferred work (if present) and why it is safe to defer
- exact test commands used for slice validation

---

## Acceptance Criteria

- every listed touchpoint is either updated or explicitly marked as no-change with justification
- the slice has at least one focused regression test proving intended behavior
- no boundary violations are introduced relative to `RESPONSIBILITY_BOUNDARIES.md`
- parent-level behavior remains compatible when this slice lands alone

---

## Atomic Work Items

1. Implement the scoped behavior in the listed touchpoints with explicit boundary ownership.
2. Add/adjust regression tests for the changed behavior and verify deterministic outcomes.
3. Record before/after evidence for the changed surface (contract, visibility, routing, or runtime behavior).
4. Document any deferred edges and why they do not block parent-task acceptance.
