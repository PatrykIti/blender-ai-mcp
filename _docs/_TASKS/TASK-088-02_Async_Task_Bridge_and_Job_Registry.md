# TASK-088-02: Async Task Bridge and Job Registry

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ✅ Done  
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
  - `tests/unit/adapters/mcp/test_background_job_registry.py`

### Scope Rule

This task owns only the server-side bridge and registry.

It does not own:

- addon job primitives
- RPC transport verbs
- tool-by-tool adoption

### Runtime Gate

- task bridge validation must run against a FastMCP runtime with task support enabled (`fastmcp[tasks]` or equivalent)
- task-launch entrypoints used for bridge tests must be `async def` with `task=True`
- bridge-owned task entrypoints must declare explicit `TaskConfig` mode semantics and document why each mode is chosen

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
- bridge behavior is validated on an async, task-capable runtime path (not sync-only stubs)

## Completion Summary

- added `server/adapters/mcp/tasks/job_registry.py`, `progress.py`, `result_store.py`, and `task_bridge.py`
- the bridge now tracks both FastMCP `task_id` and addon-side `job_id` when Blender-backed execution is used
- added runtime compatibility patching for the current FastMCP/Docket symbol drift so task progress plumbing remains usable in this repo baseline

---

## Atomic Work Items

1. Define FastMCP task ID to addon job ID mapping.
2. Add a registry that stores status, progress, cancelability, and final result metadata.
3. Keep task lifecycle coordination in adapter/infrastructure code, not in business handlers.
4. Add tests for launch, poll, completion, and cancellation bookkeeping.
