# TASK-083-01-01: Core FastMCP 3.x Dependency and Runtime Audit

**Parent:** [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

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

### Existing Files To Update

- `pyproject.toml`
  - move FastMCP dependency to a stable 3.0+ line (`>=3.0,<4.0` until explicitly revised)
  - define a separate 3.1+ feature gate for TASK-084/TASK-094 runtime work
  - record any additional dependencies only when they are actually required by selected platform features
- `README.md`
  - update the runtime baseline note so it no longer states that the repo is still anchored on 2.x
- `_docs/_MCP_SERVER/README.md`
  - add a short migration-baseline section

### New Files To Create

- `server/adapters/mcp/platform/runtime_inventory.py`
  - canonical list of current MCP surface modules, entrypoints, and compatibility constraints
- `tests/unit/adapters/mcp/test_runtime_inventory.py`
  - validates the inventory against the actual runtime layout
- `_docs/_MCP_SERVER/fastmcp_3x_migration_matrix.md`
  - maps current 2.x patterns to the target 3.x composition model
---

## Acceptance Criteria

- there is one explicit list of current MCP surfaces and entrypoints
- every known 2.x coupling point is documented and mapped to a follow-up migration task
- inventory gaps are captured as first-class work items, not left implicit
---

## Atomic Work Items

1. Inventory all area modules, including missing side-effect imports and non-tool components.
2. Inventory all router metadata families and list which MCP-facing families are absent.
3. Inventory every place that assumes one global `mcp` instance.
4. Inventory every place that assumes one flat public catalog.
5. Inventory every adapter entry point that will need async-aware context/session handling later.
