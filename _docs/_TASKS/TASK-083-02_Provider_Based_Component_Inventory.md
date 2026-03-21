# TASK-083-02: Provider-Based Component Inventory

**Parent:** [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md)

---

## Objective

Replace the current flat registration mindset with reusable provider groups that can be mounted into multiple public surfaces without duplicating handler logic.

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

---

## Provider Split

- `core_tools`
  - scene, modeling, mesh, material, uv, collection, curve, lattice, sculpt, baking, text, armature, system
- `router_tools`
  - `router_*`
- `workflow_tools`
  - `workflow_catalog`
- `internal_tools`
  - compatibility or helper tools not meant for default discovery

`server/adapters/mcp/dispatcher.py` remains the router execution bridge. It does not become the public catalog registry.

---

## Pseudocode

```python
from fastmcp.server.providers import LocalProvider


def build_core_tools_provider(di) -> LocalProvider:
    provider = LocalProvider(name="core-tools")
    register_scene_tools(provider, di)
    register_mesh_tools(provider, di)
    register_modeling_tools(provider, di)
    register_text_tools(provider, di)
    return provider
```

---

## Tests

- provider inventory coverage across all tool areas
- no-side-effect import requirement for area modules
- explicit test that `text` and `workflow_catalog` are included in the provider plan

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-083-02-01](./TASK-083-02-01_Core_Provider_Component_Inventory.md) | Core Provider-Based Component Inventory | Core implementation layer |
| [TASK-083-02-02](./TASK-083-02-02_Tests_Provider_Component_Inventory.md) | Tests and Docs Provider-Based Component Inventory | Tests, docs, and QA |

---

## Acceptance Criteria

- tools are assembled from reusable providers instead of one global registry
- multiple FastMCP servers can be composed from the same providers
- provider boundaries stay aligned with Clean Architecture responsibilities
