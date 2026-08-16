# TASK-083-06-02: Tests and Docs Platform Regression Harness and Docs

**Parent:** [TASK-083-06](./TASK-083-06_Platform_Regression_Harness_and_Docs.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-06-01](./TASK-083-06-01_Core_Platform_Regression_Harness_Docs.md)

---

## Objective

Add tests and documentation updates for **Platform Regression Harness and Docs**.

---

## Repository Touchpoints

- `tests/unit/router/adapters/test_mcp_integration.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`
- `README.md`

---

## Planned Work

### Regression Scenarios (Required)

1. baseline regression harness path: default surface bootstrap and inventory checks pass.
2. compatibility harness path: legacy-flat and llm-guided surfaces remain coexistence-safe.
3. gate enforcement path: migration gates fail loudly when composition or transform assumptions break.
4. docs accuracy path: architecture/runtime docs match tested platform behavior.

### Metrics To Capture

- platform regression suite pass rate
- gate check failure detection count during intentional break tests
- doc-to-runtime mismatch findings (target: 0)

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
