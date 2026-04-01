# TASK-093-04: Operational Status and Diagnostics Surface

**Parent:** [TASK-093](./TASK-093_Observability_Timeouts_and_Pagination.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-093-01](./TASK-093-01_Telemetry_Model_and_OpenTelemetry_Bootstrap.md), [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)

---

## Objective

Expose an operational diagnostics surface for maintainers and clients.

---

## Planned Work

- publish status data such as:
  - active surface or profile
  - active contract line
  - router summary
  - router failure policy / last failure disposition
  - task counts
  - timeout config
  - visibility phase

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-093-04-01](./TASK-093-04-01_Core_Operational_Status_Diagnostics.md) | Core Operational Status and Diagnostics Surface | Core implementation layer |
| [TASK-093-04-02](./TASK-093-04-02_Tests_Operational_Status_Diagnostics.md) | Tests and Docs Operational Status and Diagnostics Surface | Tests, docs, and QA |

---

## Acceptance Criteria

- debugging runtime state no longer requires guesswork

## Completion Summary

- `router_get_status()` now exposes active surface/profile, contract line, timeout policy, task runtime pair, telemetry bootstrap state, router failure policy, last router disposition/error, and background job summaries
- diagnostics now read from live session state and factory-attached runtime metadata instead of relying on implicit assumptions

---

## Atomic Work Items

1. Define the diagnostics payload contract.
2. Expose profile, contract line, phase, timeout, task state, and router failure policy / last failure disposition.
3. Add one test proving diagnostics reflect session-phase and profile changes.
