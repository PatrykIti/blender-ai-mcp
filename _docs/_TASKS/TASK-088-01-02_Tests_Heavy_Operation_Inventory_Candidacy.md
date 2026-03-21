# TASK-088-01-02: Tests and Docs Heavy Operation Inventory and Task Candidacy

**Parent:** [TASK-088-01](./TASK-088-01_Heavy_Operation_Inventory_and_Task_Candidacy.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-01-01](./TASK-088-01-01_Core_Heavy_Operation_Inventory_Candidacy.md)

---

## Objective

Add tests and documentation updates for **Heavy Operation Inventory and Task Candidacy**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. search/discovery happy path: expected tools are discoverable and callable through the intended public path.
2. pinned-entry behavior: pinned tools remain visible while non-pinned tools are hidden from flat listing.
3. negative query path: irrelevant query returns bounded, deterministic results without leaking hidden tools.
4. router/dispatcher parity: discovered execution path matches direct execution behavior for the same tool call.

### Metrics To Capture

- `tools/list` payload size before/after (bytes)
- visible tool count per surface profile (`legacy-flat` vs `llm-guided`)
- top-N discovery relevance sanity check on curated queries

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
