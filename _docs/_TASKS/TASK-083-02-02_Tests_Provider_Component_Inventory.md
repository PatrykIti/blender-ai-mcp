# TASK-083-02-02: Tests and Docs Provider-Based Component Inventory

**Parent:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02-01](./TASK-083-02-01_Core_Provider_Component_Inventory.md)

---

## Objective

Add tests and documentation updates for **Provider-Based Component Inventory**.

## Current State

Baseline provider inventory tests exist and pass, including registrar/provider coverage and a guard that area modules no longer depend on the global singleton decorator path.

This slice remains open because it still overhangs on explicit evidence/metrics-style documentation rather than raw code correctness alone, and because final removal of the temporary compatibility shim is intentionally deferred.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. provider inventory happy path: expected tools are registered through reusable `register_*_tools(...)` seams.
2. provider builder path: `core_tools`, `router_tools`, `workflow_tools`, and `internal_tools` build reusable `LocalProvider` instances.
3. no-singleton path: area modules no longer depend on `server.adapters.mcp.instance.mcp` or `@mcp.tool()` registration.
4. router/dispatcher parity: provider extraction does not change canonical internal tool names used by router/dispatcher paths.

### Metrics To Capture

- provider inventory pass rate across all area families
- provider builder bootstrap pass rate per provider group
- area modules still depending on global singleton registration (target: `0`)

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
