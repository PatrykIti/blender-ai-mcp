# TASK-083-02-01: Core Provider-Based Component Inventory

**Parent:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md)

---

## Objective

Implement the core code changes for **Provider-Based Component Inventory**.

---

## Repository Touchpoints

- `server/adapters/mcp/instance.py`
- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/areas/__init__.py`
- `server/infrastructure/di.py`
- `server/adapters/mcp/dispatcher.py`
- `server/application/tool_handlers/*.py`
- `server/domain/tools/*.py`

---

## Planned Work

### Existing Files To Update

- `server/adapters/mcp/areas/*.py`
  - stop assuming a single global `mcp`
  - expose registration functions that can bind to a concrete provider
- `server/adapters/mcp/areas/__init__.py`
  - replace side-effect-only imports with exported registrars/provider builders
- `server/infrastructure/di.py`
  - add provider factories alongside handler factories

### New Files To Create

- `server/adapters/mcp/providers/core_tools.py`
- `server/adapters/mcp/providers/router_tools.py`
- `server/adapters/mcp/providers/workflow_tools.py`
- `server/adapters/mcp/providers/internal_tools.py`
- `server/adapters/mcp/providers/__init__.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`

### Migration Rule

Do not rewrite every MCP area in one pass.

Provider extraction should proceed area by area in this order:

1. `scene`, `mesh`, `modeling`
2. `router`, `workflow_catalog`
3. remaining tool families

After each family:

- the provider inventory test must stay green
- dispatcher alignment must stay green
- hidden side-effect imports must keep shrinking, not regrow in another file
---

## Acceptance Criteria

- tools are assembled from reusable providers instead of one global registry
- multiple FastMCP servers can be composed from the same providers
- provider boundaries stay aligned with Clean Architecture responsibilities
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
