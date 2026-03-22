# TASK-097-01-02: Tests and Docs Correction Event Model and Audit Schema

**Parent:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01-01](./TASK-097-01-01_Core_Correction_Event_Audit_Schema.md)

---

## Objective

Add tests and documentation updates for **Correction Event Model and Audit Schema**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. schema-conformant happy path: responses validate against declared structured contracts.
2. legacy renderer path: legacy text mode remains available where required.
3. structured renderer path: structured or structured+summary outputs remain deterministic.
4. invalid payload path: schema violations fail fast with explicit contract errors.

### Metrics To Capture

- schema validation pass rate in contract tests
- structured vs legacy parity checks for key fields
- number of contract-breaking diffs detected by snapshots

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
