# Runtime Baseline Matrix

Runtime baseline for the FastMCP 3.x migration series (`TASK-083` through `TASK-097`).

## Support Policy

- Supported server baseline: Python `3.11+`
- Supported FastMCP baseline: `>=3.0,<4.0`
- Feature-gated FastMCP baseline: `>=3.1,<4.0` for Tool Search / BM25 and Code Mode work
- Python `3.10` is not part of the supported baseline for this migration series

## Matrix

| Python | FastMCP | Status | Expected capability level | Notes |
|---|---|---|---|---|
| `3.11` | `>=3.0,<3.1` | Supported | Provider/factory/transform baseline work | Gate 0 baseline for `TASK-083`; 3.1-only features remain disabled |
| `3.11` | `>=3.1,<4.0` | Supported | Baseline work plus Tool Search / BM25 and Code Mode experiments | Required runtime line for `TASK-084` and optional `TASK-094` comparison work |
| `3.12` | `>=3.0,<4.0` | Expected supported | Same as Python 3.11 baseline | Treat as compatible so long as repo tests stay green |
| `3.10` | any `3.x` | Not supported | None | Excluded because the repo's practical dependency set already requires `3.11+` for full functionality |

## Smoke-Test Expectations

Gate 0 for the migration series should evaluate the runtime baseline against these expectations:

1. Project metadata (`pyproject.toml`) matches the supported Python and FastMCP baseline.
2. Runtime inventory stays aligned with the actual MCP area layout and metadata coverage.
3. Bootstrap and factory smoke tests are added as provider/factory slices land in `TASK-083-02` and `TASK-083-03`.
4. FastMCP `3.1+`-only tasks stay blocked until the runtime line is explicitly moved to `>=3.1,<4.0`.

## Related Files

- `pyproject.toml`
- `server/adapters/mcp/platform/runtime_inventory.py`
- `_docs/_MCP_SERVER/fastmcp_3x_migration_matrix.md`
- `_docs/_TASKS/TASK-083_FastMCP_3x_Platform_Migration.md`
