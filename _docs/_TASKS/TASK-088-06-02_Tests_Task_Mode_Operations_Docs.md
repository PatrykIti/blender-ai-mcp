# TASK-088-06-02: Tests and Docs Task Mode Operations and Docs

**Parent:** [TASK-088-06](./TASK-088-06_Task_Mode_Tests_Operations_and_Docs.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-088-06-01](./TASK-088-06-01_Core_Task_Mode_Operations_Docs.md)

---

## Objective

Add tests and documentation updates for **Task Mode Tests, Operations, and Docs**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. background happy path: launch -> progress -> completion -> result retrieval works end-to-end.
2. cancellation path: cancel request stops execution and reports terminal cancelled state.
3. timeout boundary path: tool/task/RPC timeouts trigger correct boundary-specific error handling.
4. foreground compatibility path: non-task calls retain expected synchronous behavior.
5. task-mode semantics path: endpoints with `TaskConfig(mode="forbidden"|"optional"|"required")` behave exactly as configured.
6. registration guard path: `task=True` on a sync function raises registration-time error.

### Metrics To Capture

- job launch-to-first-progress latency
- cancellation acknowledgement latency
- timeout classification accuracy across MCP/task/RPC boundaries
- task-mode matrix coverage across configured endpoints
- sync-task registration violations detected (target: 0 in runtime, 1+ in dedicated negative test fixture)

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
