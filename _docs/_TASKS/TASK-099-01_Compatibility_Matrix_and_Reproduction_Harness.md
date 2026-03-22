# TASK-099-01: Compatibility Matrix and Reproduction Harness

**Parent:** [TASK-099](./TASK-099_FastMCP_Docket_Runtime_Alignment_and_Shims_Removal.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)

---

## Objective

Audit and reproduce the current FastMCP+Docket task-runtime mismatch in a stable, documented way.

---

## Repository Touchpoints

- `pyproject.toml`
- `poetry.lock`
- `server/adapters/mcp/tasks/runtime_compat.py`
- `tests/unit/adapters/mcp/test_background_job_registry.py`
- `tests/unit/adapters/mcp/test_task_mode_registration.py`

---

## Planned Work

- capture the exact FastMCP/Docket version pair currently in use
- build a dedicated reproduction test or harness for the symbol drift
- document which parts fail without the repo shim

### Current Code Reality

The current audit should start from:

- `pyproject.toml`
- `poetry.lock`
- `server/adapters/mcp/tasks/runtime_compat.py`
- `tests/unit/adapters/mcp/test_background_job_registry.py`

Right now the repo only asserts that `current_execution` gets added.
It does not yet capture a fuller reproduction matrix such as:

- task registration path
- task progress path
- task submission path under a real server/session context

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-099-01-01](./TASK-099-01-01_Core_Runtime_Version_Audit.md) | Core Runtime Version Audit | Core implementation layer |
| [TASK-099-01-02](./TASK-099-01-02_Tests_Runtime_Reproduction_Harness.md) | Tests Runtime Reproduction Harness | Tests, docs, and QA |

---

## Acceptance Criteria

- maintainers can reproduce the current drift intentionally
- the repo records the exact version pair that required the shim
