# TASK-088-04-02: Tests and Docs RPC and Blender Main-Thread Adaptation

**Parent:** [TASK-088-04](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-04-01](./TASK-088-04-01_Core_RPC_Blender_Main_Thread.md)

---

## Objective

Add tests and documentation updates for **RPC and Blender Main-Thread Adaptation**.

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
