# TASK-087-06-02: Tests and Docs Elicitation Tests and Docs

**Parent:** [TASK-087-06](./TASK-087-06_Elicitation_Tests_and_Docs.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-06-01](./TASK-087-06-01_Core_Elicitation_Tests_Docs.md)

---

## Objective

Add tests and documentation updates for **Elicitation Tests and Docs**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. accept flow: missing parameters resolved through structured elicitation and execution continues.
2. decline flow: user decline is preserved with stable status and no unsafe auto-execution.
3. cancel flow: cancellation state is persisted and retry behaves deterministically.
4. fallback path: tool-only client receives typed `needs_input` payload equivalent to native elicitation.

### Metrics To Capture

- resolution completion rate for elicited fields
- mean elicitation rounds to completion
- fallback/native parity mismatches (target: 0)

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
