# TASK-093-02: Tool and Task Timeout Policy

**Parent:** [TASK-093](./TASK-093_Observability_Timeouts_and_Pagination.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md)

---

## Objective

Define separate timeout policy for foreground tools, background tasks, RPC calls, and Blender-side execution.

---

## Repository Touchpoints

- `server/adapters/rpc/client.py`
- `blender_addon/infrastructure/rpc_server.py`
- `server/infrastructure/config.py`

---

## Acceptance Criteria

- every runtime boundary has an explicit timeout contract
