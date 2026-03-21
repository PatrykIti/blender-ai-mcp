# TASK-088-02: Async Task Bridge and Job Registry

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-01](./TASK-088-01_Heavy_Operation_Inventory_and_Task_Candidacy.md)

---

## Objective

Build the FastMCP task bridge and a job registry for long-running operations.

---

## Planned Work

- create:
  - `server/adapters/mcp/tasks/job_registry.py`
  - `server/adapters/mcp/tasks/task_bridge.py`
  - `tests/unit/adapters/mcp/test_job_registry.py`

---

## Pseudocode

```python
@provider.tool(task=True)
async def render_angles_task(...):
    job = await registry.start(...)
    ...
```

---

## Acceptance Criteria

- the server can register, track, and complete background jobs explicitly
