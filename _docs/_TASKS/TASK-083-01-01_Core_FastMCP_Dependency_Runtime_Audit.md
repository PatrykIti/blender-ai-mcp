# TASK-083-01-01: Core FastMCP 3.x Dependency and Runtime Audit

**Parent:** [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md)  

---

## Objective

Implement the core code changes for **FastMCP 3.x Dependency and Runtime Audit**.

---

## Repository Touchpoints

- `pyproject.toml`
- `server/main.py`
- `server/adapters/mcp/instance.py`
- `server/adapters/mcp/server.py`
- `server/adapters/mcp/areas/__init__.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/adapters/mcp_integration.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
