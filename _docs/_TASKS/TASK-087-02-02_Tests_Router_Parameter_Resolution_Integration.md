# TASK-087-02-02: Tests and Docs Router Parameter Resolution Integration

**Parent:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-02-01](./TASK-087-02-01_Core_Router_Parameter_Resolution_Integration.md)

---

## Objective

Add tests and documentation updates for **Router Parameter Resolution Integration**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. router resolution happy path: parameter resolver + elicitation integration resolves required fields.
2. partial answer path: stored partial inputs are reused on follow-up interaction.
3. invalid input path: bad values return typed unresolved entries without silent coercion.
4. fallback path: tool-only clients receive equivalent `needs_input` contract.

### Metrics To Capture

- parameter resolution completion rate
- invalid-input recovery success rate
- native-vs-fallback unresolved payload parity mismatches (target: 0)

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
