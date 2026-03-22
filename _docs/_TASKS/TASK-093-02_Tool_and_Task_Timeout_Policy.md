# TASK-093-02: Tool and Task Timeout Policy

**Parent:** [TASK-093](./TASK-093_Observability_Timeouts_and_Pagination.md)  
**Status:** 🚧 In Progress  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md)

---

## Objective

Define separate timeout policy for foreground tools, background tasks, RPC calls, and Blender-side execution.

---

## Ownership Rule

This task defines:

- timeout boundary names
- default timeout classes
- override rules
- timeout-related diagnostics fields

This task does not define:

- RPC launch / poll / cancel verbs
- addon job lifecycle primitives
- tool-by-tool task adoption

Those belong to TASK-088 and must consume the timeout policy defined here.

---

## Repository Touchpoints

- `server/adapters/rpc/client.py`
- `blender_addon/infrastructure/rpc_server.py`
- `server/infrastructure/config.py`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-093-02-01](./TASK-093-02-01_Core_Timeout.md) | Core Tool and Task Timeout Policy | Core implementation layer |
| [TASK-093-02-02](./TASK-093-02-02_Tests_Timeout.md) | Tests and Docs Tool and Task Timeout Policy | Tests, docs, and QA |

---

## Acceptance Criteria

- every runtime boundary has an explicit timeout contract
