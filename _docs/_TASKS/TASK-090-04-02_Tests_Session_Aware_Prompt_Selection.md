# TASK-090-04-02: Tests and Docs Session-Aware Prompt Selection

**Parent:** [TASK-090-04](./TASK-090-04_Session_Aware_Prompt_Selection.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-090-04-01](./TASK-090-04-01_Core_Session_Aware_Prompt_Selection.md)

---

## Objective

Add tests and documentation updates for **Session-Aware Prompt Selection**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. native prompt path: prompt-capable clients can list and render prompts correctly.
2. bridge path: tool-only clients can access prompts through bridge tools.
3. phase-aware selection path: recommended prompt set changes with session phase/profile.
4. missing argument path: prompt rendering fails with deterministic validation errors.

### Metrics To Capture

- prompt render success rate by profile
- prompt bridge parity mismatches vs native prompts (target: 0)
- prompt catalog coverage by tagged audience/phase

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
