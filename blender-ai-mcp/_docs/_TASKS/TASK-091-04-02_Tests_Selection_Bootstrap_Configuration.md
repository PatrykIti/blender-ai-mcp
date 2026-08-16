# TASK-091-04-02: Tests and Docs Client Selection and Bootstrap Configuration

**Parent:** [TASK-091-04](./TASK-091-04_Client_Selection_and_Bootstrap_Configuration.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-091-04-01](./TASK-091-04-01_Core_Selection_Bootstrap_Configuration.md)

---

## Objective

Add tests and documentation updates for **Client Selection and Bootstrap Configuration**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. selection happy path: bootstrap config selects intended profile + contract line.
2. override path: explicit runtime selection overrides defaults deterministically.
3. invalid selection path: unsupported profile/version requests fail with clear errors.
4. compatibility path: client selection does not leak wrong-version components.

### Metrics To Capture

- selection matrix coverage across supported profiles
- invalid-selection error contract pass rate
- profile/version leakage count (target: 0)

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
