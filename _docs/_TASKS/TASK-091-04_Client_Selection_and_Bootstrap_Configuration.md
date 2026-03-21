# TASK-091-04: Client Selection and Bootstrap Configuration

**Parent:** [TASK-091](./TASK-091_Versioned_Client_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-091-03](./TASK-091-03_Version_Filtered_Server_Composition.md)

---

## Objective

Make the active surface variant selectable through bootstrap and runtime configuration.

---

## Planned Work

- update:
  - `server/infrastructure/config.py`
  - `server/main.py`
- add environment variables such as:
  - `MCP_SURFACE_PROFILE`
  - `MCP_DEFAULT_CONTRACT_LINE`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-091-04-01](./TASK-091-04-01_Core_Selection_Bootstrap_Configuration.md) | Core Client Selection and Bootstrap Configuration | Core implementation layer |
| [TASK-091-04-02](./TASK-091-04-02_Tests_Selection_Bootstrap_Configuration.md) | Tests and Docs Client Selection and Bootstrap Configuration | Tests, docs, and QA |

---

## Acceptance Criteria

- the chosen surface variant is explicit and configurable

---

## Atomic Work Items

1. Add explicit profile selection at bootstrap.
2. Add optional default contract-line selection.
3. Surface both values in diagnostics and startup logs.
