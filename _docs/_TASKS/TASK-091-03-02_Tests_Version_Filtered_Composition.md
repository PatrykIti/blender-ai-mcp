# TASK-091-03-02: Tests and Docs Version-Filtered Server Composition

**Parent:** [TASK-091-03](./TASK-091-03_Version_Filtered_Server_Composition.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-091-03-01](./TASK-091-03-01_Core_Version_Filtered_Composition.md)

---

## Objective

Add tests and documentation updates for **Version-Filtered Server Composition**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. version filter happy path: expected contract versions are exposed per profile.
2. coexistence path: multiple versions of one capability coexist without handler duplication.
3. selection path: bootstrap/profile config selects intended contract line.
4. leakage path: unversioned or wrong-version components do not leak into filtered surfaces.

### Metrics To Capture

- component counts by version and profile
- version-filter mismatch count in regression tests (target: 0)
- legacy-to-llm migration coverage for versioned capabilities

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
