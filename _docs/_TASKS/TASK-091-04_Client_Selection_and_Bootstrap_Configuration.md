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
- add an environment variable such as `MCP_SURFACE_PROFILE`

---

## Acceptance Criteria

- the chosen surface variant is explicit and configurable
