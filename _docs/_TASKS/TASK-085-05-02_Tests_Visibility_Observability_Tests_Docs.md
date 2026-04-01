# TASK-085-05-02: Tests and Docs Visibility Observability, Tests, and Docs

**Parent:** [TASK-085-05](./TASK-085-05_Visibility_Observability_Tests_and_Docs.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-05-01](./TASK-085-05-01_Core_Visibility_Observability_Tests_Docs.md)

---

## Objective

Add tests and documentation updates for **Visibility Observability, Tests, and Docs**.

## Completion Summary

This slice is now closed.

- tests cover guided visibility diagnostics and native session visibility application
- product docs now explain the current guided-mode visibility baseline

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. profile-only visibility: each profile exposes the expected capability subset.
2. phase transition visibility: session phase changes update visible components deterministically.
3. tag conflict behavior: overlapping tags resolve by defined policy order.
4. regression path: disabled components cannot be executed through listed/public entry points.

### Metrics To Capture

- component counts per profile and per phase
- number of visibility policy mismatches in regression suite (target: 0)
- time from phase update to reflected listing change

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
