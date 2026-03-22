# TASK-099-01-01: Core Runtime Version Audit

**Parent:** [TASK-099-01](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-01](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md)

---

## Objective

Audit the currently installed FastMCP and Docket versions and tie them to the repo-local compatibility shim.

---

## Repository Touchpoints

- `pyproject.toml`
- `poetry.lock`
- `server/adapters/mcp/tasks/runtime_compat.py`

---

## Planned Work

- document the exact repo baseline
- document why the shim exists
- identify the upstream symbol/API mismatch precisely

### Audit Detail

- record the currently locked FastMCP version from `poetry.lock`
- record the currently resolved Docket / `pydocket` line from the environment and lockfile context
- map which symbol/API names differ:
  - `current_execution`
  - `current_docket`
  - `current_worker`
- identify whether the mismatch is limited to naming drift or includes behavior/contract drift

---

## Acceptance Criteria

- the repo baseline and the mismatch are described in one stable audit slice
