# TASK-093-04-01: Core Operational Status and Diagnostics Surface

**Parent:** [TASK-093-04](./TASK-093-04_Operational_Status_and_Diagnostics_Surface.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-093-01](./TASK-093-01_Telemetry_Model_and_OpenTelemetry_Bootstrap.md), [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)

---

## Objective

Implement the core code changes for **Operational Status and Diagnostics Surface**.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/infrastructure/config.py`
- `server/infrastructure/telemetry.py`
- `server/adapters/mcp/tasks/job_registry.py`
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

## Acceptance Criteria

- debugging runtime state no longer requires guesswork
---

## Atomic Work Items

1. Define the diagnostics payload contract.
2. Expose profile, contract line, phase, timeout, task state, and router failure policy / last failure disposition.
3. Add one test proving diagnostics reflect session-phase and profile changes.
