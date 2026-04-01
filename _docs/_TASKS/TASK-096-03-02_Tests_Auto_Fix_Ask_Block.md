# TASK-096-03-02: Tests and Docs Auto-Fix, Ask, Block Policy Engine

**Parent:** [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-096-03-01](./TASK-096-03-01_Core_Auto_Fix_Ask_Block.md)

---

## Objective

Add tests and documentation updates for **Auto-Fix, Ask, Block Policy Engine**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. auto-fix decision path: high-confidence low-risk deterministic corrections resolve to `auto-fix`.
2. ask decision path: medium-confidence or bounded-ambiguity corrections resolve to `ask` (elicitation/escalation path).
3. block decision path: low/none confidence or forbidden-risk combinations resolve to `block`.
4. precedence path: risk and correction-type guards override raw confidence when policy rules conflict.

### Metrics To Capture

- decision-matrix coverage across correction type x risk x confidence combinations
- policy-branch coverage for `auto-fix`, `ask`, and `block`
- unexpected default/fallback decision count (target: 0)

### Documentation Deliverables

- update task-linked docs with a before/after summary tied to the captured metrics
- document exact test commands, fixtures, and profile/config used during validation
- record compatibility or migration notes when behavior differs between surfaces

---

## Acceptance Criteria

- all required regression scenarios are implemented and passing in CI/local test runs
- metrics are captured with baseline vs post-change values and attached to the task update
- docs include the regression matrix and explain expected behavior boundaries
- no untracked regressions are observed on related correction-policy and elicitation escalation paths

---

## Atomic Work Items

1. Implement the required regression scenarios in focused unit/integration tests.
2. Run the target suites, collect metric outputs, and compare to baseline values.
3. Update docs with regression matrix, metric table, and migration/compatibility notes.
4. Verify adjacent surfaces for spillover regressions and document the result.
