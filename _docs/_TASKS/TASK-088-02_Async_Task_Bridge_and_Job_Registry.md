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

### Identity Rule

Track both:

- FastMCP task ID
- addon-side Blender job ID

The bridge is not complete if only one of these identities exists.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-088-02-01](./TASK-088-02-01_Core_Async_Bridge_Job_Registry.md) | Core Async Task Bridge and Job Registry | Core implementation layer |
| [TASK-088-02-02](./TASK-088-02-02_Tests_Async_Bridge_Job_Registry.md) | Tests and Docs Async Task Bridge and Job Registry | Tests, docs, and QA |

---

## Acceptance Criteria

- the server can register, track, and complete background jobs explicitly

---

## Atomic Work Items

1. Define FastMCP task ID to addon job ID mapping.
2. Add a registry that stores status, progress, cancelability, and final result metadata.
3. Add tests for launch, poll, completion, and cancellation bookkeeping.
