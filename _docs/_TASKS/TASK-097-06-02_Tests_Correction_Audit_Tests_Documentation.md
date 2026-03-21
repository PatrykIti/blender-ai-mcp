# TASK-097-06-02: Tests and Docs Correction Audit Tests and Documentation

**Parent:** [TASK-097-06](./TASK-097-06_Correction_Audit_Tests_and_Documentation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-097-06-01](./TASK-097-06-01_Core_Correction_Audit_Tests_Documentation.md)

---

## Objective

Add tests and documentation updates for **Correction Audit Tests and Documentation**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. policy happy path: confidence+risk inputs resolve to expected auto-fix/ask/block decision.
2. medium-confidence path: escalation invokes clarification flow instead of silent rewrite.
3. audit path: correction events and execution reports are emitted with required fields.
4. postcondition path: high-risk fixes are verified and failures are surfaced explicitly.

### Metrics To Capture

- decision-matrix coverage across risk/confidence classes
- audit event completeness ratio
- postcondition verification success/failure distribution

### Documentation Deliverables

- update task-linked docs with a before/after summary tied to the captured metrics
- document exact test commands, fixtures, and profile/config used during validation
- record compatibility or migration notes when behavior differs between surfaces

---

## Acceptance Criteria

- all required regression scenarios are implemented and passing in CI/local test runs
- metrics are captured with baseline vs post-change values and attached to the task update
- docs include the regression matrix and explain expected behavior boundaries
- no untracked regressions are observed on related router/dispatcher/platform paths

---

## Atomic Work Items

1. Implement the required regression scenarios in focused unit/integration tests.
2. Run the target suites, collect metric outputs, and compare to baseline values.
3. Update docs with regression matrix, metric table, and migration/compatibility notes.
4. Verify adjacent surfaces for spillover regressions and document the result.
