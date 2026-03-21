# TASK-088-02-01: Core Async Task Bridge and Job Registry

**Parent:** [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-01](./TASK-088-01_Heavy_Operation_Inventory_and_Task_Candidacy.md)

---

## Objective

Implement the core code changes for **Async Task Bridge and Job Registry**.

---

## Repository Touchpoints

- `server/adapters/mcp/tasks/job_registry.py`
- `server/adapters/mcp/tasks/task_bridge.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/extraction.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `tests/unit/adapters/mcp/test_job_registry.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/tasks/job_registry.py`
  - `server/adapters/mcp/tasks/task_bridge.py`
  - `tests/unit/adapters/mcp/test_job_registry.py`

### Scope Rule

This task owns only the server-side bridge and registry.

It does not own:

- addon job primitives
- RPC transport verbs
- tool-by-tool adoption
---

## Acceptance Criteria

- the server can register, track, and complete background jobs explicitly
---

## Atomic Work Items

1. Implement one server-side job registry keyed by FastMCP task identity and capable of storing addon job identity when present.
2. Implement one adapter-side task bridge that launches, polls, and finalizes background-capable entry tools without pushing task lifecycle logic into handlers.
3. Prove the bridge works for one render-capable entry point and one non-render background candidate before wider adoption.
