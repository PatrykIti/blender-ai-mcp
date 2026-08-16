# Runtime Baseline Matrix

Runtime baseline for the FastMCP 3.x migration series (`TASK-083` through `TASK-099`).

## Support Policy

- Supported server baseline: Python `3.11+`
- Supported task-capable runtime pair: `fastmcp 3.2.4` + `pydocket 0.19.x`
- Supported FastMCP line for current task-mode platform work: `3.2.x`
- Code Mode sandbox extra: `pydantic-monty==0.0.11`
- Python `3.10` is not part of the supported baseline for this migration series

## Matrix

| Python | FastMCP / Docket | Status | Expected capability level | Notes |
|---|---|---|---|---|
| `3.11` | `fastmcp 3.2.4` + `pydocket 0.19.x` | Supported | Full current platform baseline including task mode and Streamable HTTP guided state hardening | Explicit aligned pair validated during the 2026-04-28 streamable hardening work |
| `3.11` | `fastmcp 3.2.x` + `pydocket 0.19.x` | Expected compatible | Same as validated pair | Treat as candidate line, but keep validation centered on the locked pair |
| `3.12` | `fastmcp 3.2.x` + `pydocket 0.19.x` | Expected supported | Same as Python 3.11 baseline | Treat as compatible so long as repo tests stay green |
| `3.10` | any `3.x` | Not supported | None | Excluded because the repo's practical dependency set already requires `3.11+` for full functionality |

## Smoke-Test Expectations

Gate 0 for the migration series should evaluate the runtime baseline against these expectations:

1. Project metadata (`pyproject.toml`) matches the supported Python and task-runtime pair.
2. Runtime inventory stays aligned with the actual MCP area layout and metadata coverage.
3. Bootstrap/factory/provider/transform smoke tests are covered by the TASK-083 regression harness.
4. Task-capable surfaces fail clearly if the resolved FastMCP+Docket pair is outside the supported line.
5. Streamable HTTP guided regression coverage confirms same-session visibility/state finalizers return before the tool response completes.

## Related Files

- `pyproject.toml`
- `server/adapters/mcp/platform/runtime_inventory.py`
- `_docs/_MCP_SERVER/fastmcp_3x_migration_matrix.md`
- `_docs/_TASKS/TASK-083_FastMCP_3x_Platform_Migration.md`
