# TASK-087-04-02: Tests and Docs Session Persistence, Retry, and Cancel Semantics

**Parent:** [TASK-087-04](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-04-01](./TASK-087-04-01_Core_Session_Persistence_Retry_Cancel.md)

---

## Objective

Add tests and documentation updates for **Session Persistence, Retry, and Cancel Semantics**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. resume path: pending elicitation state survives to the next request and resumes with the same question-set identity.
2. retry path: retrying with partial answers preserves already accepted values and only asks for unresolved fields.
3. cancel path: cancel clears pending state deterministically and prevents stale follow-up execution.
4. compatibility path: non-elicitation surfaces keep stable typed `needs_input` fallback behavior.

### Metrics To Capture

- elicitation resume success rate across request boundaries
- stale pending-state leakage count (target: 0)
- cancel cleanup correctness rate (pending ids/questions removed as expected)

### Documentation Deliverables

- update task-linked docs with a before/after summary tied to the captured metrics
- document exact test commands, fixtures, and profile/config used during validation
- record compatibility or migration notes when behavior differs between surfaces

---

## Acceptance Criteria

- all required regression scenarios are implemented and passing in CI/local test runs
- metrics are captured with baseline vs post-change values and attached to the task update
- docs include the regression matrix and explain expected behavior boundaries
- no untracked regressions are observed on related router/elicitation/session-state paths

---

## Atomic Work Items

1. Implement the required regression scenarios in focused unit/integration tests.
2. Run the target suites, collect metric outputs, and compare to baseline values.
3. Update docs with regression matrix, metric table, and migration/compatibility notes.
4. Verify adjacent surfaces for spillover regressions and document the result.
