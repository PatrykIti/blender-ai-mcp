# TASK-083-01: FastMCP 3.x Dependency and Runtime Audit

**Parent:** [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Audit every place where the current server is still shaped around FastMCP 2.x assumptions and create a migration-readiness baseline before any provider or transform refactor starts.

---

## Why

Without this audit the migration can easily become half-upgraded:

- `pyproject.toml` moves to 3.x while bootstrap still depends on 2.x patterns
- some tools are mounted through providers while others still depend on side-effect imports
- tests continue asserting flat-catalog behavior
- router/dispatcher logic still treats MCP wrappers as the only source of truth

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
- `tests/unit/router/adapters/test_mcp_integration.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

---

## Planned Work

### Existing Files To Update

- `pyproject.toml`
  - move FastMCP dependency to a stable 3.x line
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

## Technical Notes

This audit must explicitly capture already-visible inventory gaps in the repo, for example:

- `server/adapters/mcp/areas/__init__.py` does not import `text`
- `server/router/infrastructure/metadata_loader.py` does not include every MCP-facing area family

These are not side observations. They directly affect later provider inventory, discovery, and visibility work.

---

## Pseudocode

```python
@dataclass(frozen=True)
class SurfaceModule:
    area: str
    import_path: str
    public: bool
    router_callable: bool


def build_runtime_inventory() -> list[SurfaceModule]:
    return [
        SurfaceModule("scene", "server.adapters.mcp.areas.scene", True, True),
        SurfaceModule("mesh", "server.adapters.mcp.areas.mesh", True, True),
        SurfaceModule("text", "server.adapters.mcp.areas.text", True, True),
        SurfaceModule("workflow_catalog", "server.adapters.mcp.areas.workflow_catalog", True, False),
    ]
```

---

## Tests

- inventory completeness test for all current MCP areas
- inventory vs metadata-loader area coverage test
- bootstrap smoke test proving imports no longer depend on hidden side effects

---

## Acceptance Criteria

- there is one explicit list of current MCP surfaces and entrypoints
- every known 2.x coupling point is documented and mapped to a follow-up migration task
- inventory gaps are captured as first-class work items, not left implicit
