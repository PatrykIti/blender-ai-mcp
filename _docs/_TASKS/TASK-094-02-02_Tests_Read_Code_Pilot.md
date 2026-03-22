# TASK-094-02-02: Tests and Docs Read-Only Code Mode Pilot Surface

**Parent:** [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-02-01](./TASK-094-02-01_Core_Read_Code_Pilot.md)

---

## Objective

Add tests and documentation updates for **Read-Only Code Mode Pilot Surface**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. read-only happy path: code mode can orchestrate approved read workflows.
2. guardrail path: write/destructive operations are blocked in the pilot surface.
3. raw-execution guardrail path: raw Python / `bpy` execution is unavailable on the pilot surface.
4. discovery flow path: search/schema/execute loop returns deterministic outputs.
5. fallback comparison path: classic tool loop still works for same benchmark scenarios.

### Metrics To Capture

- round-trip count per benchmark scenario (code mode vs classic)
- token/context footprint estimate per scenario
- guardrail breach count in pilot tests (target: 0)

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
