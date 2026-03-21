# TASK-084-04-02: Tests and Docs Search Execution and Router-Aware Call Path

**Parent:** [TASK-084-04](./TASK-084-04_Search_Execution_and_Router_Aware_Call_Path.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-04-01](./TASK-084-04-01_Core_Search_Execution_Router_Aware.md)

---

## Objective

Add tests and documentation updates for **Search Execution and Router-Aware Call Path**.

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
5. auth/visibility parity: tools hidden by auth/visibility/session rules do not appear in `search_tools` and cannot be invoked through `call_tool`.

### Metrics To Capture

- `tools/list` payload size before/after (bytes)
- visible tool count per surface profile (`legacy-flat` vs `llm-guided`)
- top-N discovery relevance sanity check on curated queries
- hidden-tool leak count through discovery path (target: 0)

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
