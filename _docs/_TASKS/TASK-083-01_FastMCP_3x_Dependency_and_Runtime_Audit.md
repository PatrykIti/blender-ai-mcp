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
- FastMCP is upgraded while the repo still advertises or tests against a Python/runtime baseline that does not actually support the intended feature set
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
  - move FastMCP dependency to a stable 3.0+ line (`>=3.0,<4.0` until explicitly revised)
  - align `requires-python` and documented runtime support with the practical baseline used by this task series (`3.11+` unless explicitly revised)
  - define a separate 3.1+ feature gate for TASK-084/TASK-094 runtime work
  - record any additional dependencies only when they are actually required by selected platform features
  - capture any intentionally degraded or unsupported behavior on older interpreters in a runtime matrix instead of leaving it implicit
- `README.md`
  - update the runtime baseline note so it no longer states that the repo is still anchored on 2.x
  - align the documented Python/runtime baseline with the audited support matrix
- `_docs/_MCP_SERVER/README.md`
  - add a short migration-baseline section
  - add a runtime-baseline section covering interpreter support and feature gates

### New Files To Create

- `server/adapters/mcp/platform/runtime_inventory.py`
  - canonical list of current MCP surface modules, entrypoints, and compatibility constraints
- `tests/unit/adapters/mcp/test_runtime_inventory.py`
  - validates the inventory against the actual runtime layout
- `_docs/_MCP_SERVER/fastmcp_3x_migration_matrix.md`
  - maps current 2.x patterns to the target 3.x composition model
- `_docs/_MCP_SERVER/runtime_baseline_matrix.md`
  - records supported Python/FastMCP combinations, feature gates, and smoke-test expectations

---

## Technical Notes

This audit must explicitly capture already-visible inventory gaps in the repo, for example:

- side-effect area imports are still a bootstrap coupling risk and must be inventoried even when a family is currently imported
- `server/router/infrastructure/metadata_loader.py` does not include every MCP-facing area family
- sync adapter tools currently depend on ad hoc `ctx.info()` bridging instead of a broader context/session model
- the runtime still has no explicit distinction between surface profile, contract version, and session phase

These are not side observations. They directly affect later provider inventory, discovery, and visibility work.

The audit must also explicitly resolve the current Python baseline mismatch:

- repo guidance treats Python `3.11+` as the practical baseline for full functionality
- `pyproject.toml` still advertises `^3.10`
- several semantic/runtime dependencies only install on `3.11+`

Gate 0 should not be considered green until that mismatch is documented and resolved into one explicit support policy.

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
- smoke-test matrix proving the selected FastMCP line boots on the supported Python baseline(s)

---

## Atomic Work Items

1. Inventory all area modules, including missing side-effect imports and non-tool components.
2. Inventory all router metadata families and list which MCP-facing families are absent.
3. Inventory every place that assumes one global `mcp` instance.
4. Inventory every place that assumes one flat public catalog.
5. Inventory every adapter entry point that will need async-aware context/session handling later.
6. Inventory the practical Python/runtime baseline and document which feature sets are supported on each tested combination.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-083-01-01](./TASK-083-01-01_Core_FastMCP_Dependency_Runtime_Audit.md) | Core FastMCP 3.x Dependency and Runtime Audit | Core implementation layer |
| [TASK-083-01-02](./TASK-083-01-02_Tests_FastMCP_Dependency_Runtime_Audit.md) | Tests and Docs FastMCP 3.x Dependency and Runtime Audit | Tests, docs, and QA |

---

## Acceptance Criteria

- there is one explicit list of current MCP surfaces and entrypoints
- every known 2.x coupling point is documented and mapped to a follow-up migration task
- inventory gaps are captured as first-class work items, not left implicit
- FastMCP runtime baseline is pinned to an explicit 3.0+ line, with 3.1-only features documented as separate gates
- `requires-python`, docs, and smoke-test assumptions agree on the supported runtime baseline used for this migration series
