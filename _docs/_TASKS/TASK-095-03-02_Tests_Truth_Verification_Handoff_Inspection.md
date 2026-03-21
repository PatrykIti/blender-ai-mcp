# TASK-095-03-02: Tests and Docs Truth and Verification Handoff to Inspection Contracts

**Parent:** [TASK-095-03](./TASK-095-03_Truth_and_Verification_Handoff_to_Inspection_Contracts.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-095-03-01](./TASK-095-03-01_Core_Truth_Verification_Handoff_Inspection.md)

---

## Objective

Add tests and documentation updates for **Truth and Verification Handoff to Inspection Contracts**.

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
