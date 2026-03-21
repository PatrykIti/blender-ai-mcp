# TASK-088-02-02: Tests and Docs Async Task Bridge and Job Registry

**Parent:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-02-01](./TASK-088-02-01_Core_Async_Bridge_Job_Registry.md)

---

## Objective

Add tests and documentation updates for **Async Task Bridge and Job Registry**.

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
5. mode semantics path: `TaskConfig(mode="forbidden"|"optional"|"required")` behavior is consistent with bridge lifecycle expectations.

### Metrics To Capture

- job launch-to-first-progress latency
- cancellation acknowledgement latency
- timeout classification accuracy across MCP/task/RPC boundaries

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
