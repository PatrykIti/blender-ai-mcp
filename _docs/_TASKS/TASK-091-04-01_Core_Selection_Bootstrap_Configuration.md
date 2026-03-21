# TASK-091-04-01: Core Client Selection and Bootstrap Configuration

**Parent:** [TASK-091-04](./TASK-091-04_Client_Selection_and_Bootstrap_Configuration.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-091-03](./TASK-091-03_Version_Filtered_Server_Composition.md)

---

## Objective

Implement the core code changes for **Client Selection and Bootstrap Configuration**.

---

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/main.py`
- `server/adapters/mcp/settings.py`
- `server/adapters/mcp/surfaces.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
---

## Planned Work

- update:
  - `server/infrastructure/config.py`
  - `server/main.py`
- add environment variables such as:
  - `MCP_SURFACE_PROFILE`
  - `MCP_DEFAULT_CONTRACT_LINE`
---

## Acceptance Criteria

- the chosen surface variant is explicit and configurable
---

## Atomic Work Items

1. Add explicit profile selection at bootstrap.
2. Add optional default contract-line selection.
3. Surface both values in diagnostics and startup logs.