# TASK-087-05-02: Tests and Docs Tool-Only Fallback and Compatibility Mode

**Parent:** [TASK-087-05](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-05-01](./TASK-087-05-01_Core_Fallback_Compatibility.md)

---

## Objective

Add tests and documentation updates for **Tool-Only Fallback and Compatibility Mode**.

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
