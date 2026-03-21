# TASK-093-02-01: Core Tool and Task Timeout Policy

**Parent:** [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)  

---

## Objective

Implement the core code changes for **Tool and Task Timeout Policy**.

---

## Repository Touchpoints

- `server/adapters/rpc/client.py`
- `blender_addon/infrastructure/rpc_server.py`
- `server/infrastructure/config.py`
- `server/adapters/mcp/factory.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-093-02-01-01](./TASK-093-02-01-01_Platform_Timeout_Policy_and_Config.md) | Platform Timeout Policy and Config | Core slice |
| [TASK-093-02-01-02](./TASK-093-02-01-02_RPC_and_Addon_Timeout_Coordination.md) | RPC and Addon Timeout Coordination | Core slice |

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
