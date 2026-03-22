# TASK-086-03-02: Tests and Docs LLM-First Surface Simplification and Hidden Args

**Parent:** [TASK-086-03](./TASK-086-03_LLM_First_Surface_Simplification_and_Hidden_Args.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-03-01](./TASK-086-03-01_Core_LLM_Simplification_Hidden_Args.md)

---

## Objective

Add tests and documentation updates for **LLM-First Surface Simplification and Hidden Args**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. public alias happy path: aliased tool/arg names execute correct internal capability.
2. hidden argument path: hidden/internal args are injected safely and not exposed publicly.
3. invalid alias path: unknown alias fails with deterministic error contract.
4. compatibility path: canonical internal names still work for router/dispatcher internals.

### Metrics To Capture

- alias mapping coverage (tools + args)
- number of leaked hidden arguments in public schemas (target: 0)
- router/dispatcher mismatch count for aliased calls (target: 0)

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
