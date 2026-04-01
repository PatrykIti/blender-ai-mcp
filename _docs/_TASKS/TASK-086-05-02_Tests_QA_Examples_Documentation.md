# TASK-086-05-02: Tests and Docs Surface QA, Examples, and Documentation

**Parent:** [TASK-086-05](./TASK-086-05_Surface_QA_Examples_and_Documentation.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-086-05-01](./TASK-086-05-01_Core_QA_Examples_Documentation.md)

---

## Objective

Add tests and documentation updates for **Surface QA, Examples, and Documentation**.

## Completion Summary

This slice is now closed.

- docs-consistency tests now guard the current public alias examples
- the `llm-guided` public docs are synchronized across README, MCP docs, tools summary, and prompt templates

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. qa example happy path: example prompts/tool calls map to expected public aliases.
2. misuse path: invalid alias/arg examples produce deterministic guidance/errors.
3. compatibility path: qa examples remain valid for both legacy and llm-guided surfaces.
4. documentation path: examples stay synchronized with current manifest rules.

### Metrics To Capture

- example execution pass rate
- example-to-manifest drift count (target: 0)
- legacy vs llm-guided example compatibility coverage

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
