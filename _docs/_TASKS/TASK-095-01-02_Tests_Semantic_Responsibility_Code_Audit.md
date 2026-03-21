# TASK-095-01-02: Tests and Docs Semantic Responsibility Policy and Code Audit

**Parent:** [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-095-01-01](./TASK-095-01-01_Core_Semantic_Responsibility_Code_Audit.md)

---

## Objective

Add tests and documentation updates for **Semantic Responsibility Policy and Code Audit**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. allowed-role path: LaBSE remains limited to semantic retrieval/matching responsibilities.
2. discovery handoff path: platform search handles general tool discovery.
3. truth path: verification decisions use inspection contracts, not semantic confidence alone.
4. boundary regression path: semantic boundary violations are detected by tests/telemetry.

### Metrics To Capture

- boundary violation count (target: 0)
- percentage of discovery requests served by platform search path
- verification decisions backed by inspection contracts

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
