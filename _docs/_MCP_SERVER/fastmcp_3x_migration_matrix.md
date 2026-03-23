# FastMCP 3.x Migration Matrix

Canonical migration matrix for `TASK-083-01`.

Use this document together with `server/adapters/mcp/platform/runtime_inventory.py` to keep the platform migration grounded in explicit coupling points instead of implicit runtime assumptions.

## Baseline Policy

- Python support for the migration series is `3.11+`
- FastMCP baseline for the migration series is `>=3.0,<4.0`
- FastMCP `>=3.1,<4.0` is a feature gate for Tool Search / BM25 (`TASK-084`) and Code Mode (`TASK-094`)

## Runtime State After TASK-083

| Location | State after migration | Follow-up |
|---|---|---|
| `pyproject.toml` | Explicit Python/FastMCP baseline for the migration series | `TASK-084` / `TASK-094` still require moving the active runtime line to `>=3.1,<4.0` |
| `server/adapters/mcp/server.py` | Startup delegates to `build_server(surface_profile=...)` | none in `TASK-083` |
| `server/adapters/mcp/areas/__init__.py` | Explicit registrar exports only; no side-effect bootstrap imports | none in `TASK-083` |
| `server/adapters/mcp/areas/*.py` | Plain tool callables plus `register_*_tools(...)` seams; no global singleton registration | none in `TASK-083` |
| `server/adapters/mcp/context_utils.py` | Best-effort sync notifications plus session/progress bridge helpers | `TASK-087`, `TASK-088`, `TASK-093` extend richer interaction patterns |
| `server/adapters/mcp/router_helper.py` | Router-aware execution still lives in adapter helpers, outside transform/runtime ownership | `TASK-095`, `TASK-096`, `TASK-097` |
| `server/router/adapters/mcp_integration.py` | Composed-surface baseline works, but structured execution/report alignment continues | `TASK-089` |
| `server/router/infrastructure/metadata_loader.py` | Metadata coverage gaps remain explicit and audited | `TASK-084`, `TASK-086` |

## Post-TASK-083 Follow-Through

| Item | Current state | Why it matters |
|---|---|---|
| Decorator shim removal | Completed; runtime composition no longer depends on `server/adapters/mcp/instance.py` | Confirms the migration no longer keeps a transitional singleton/decorator seam alive |
| Router execution ownership coupling | Router-aware execution still routes through adapter helper code instead of a platform-owned execution layer | Still worth documenting, but no longer blocks the TASK-083 baseline closure |

## Source Of Truth

For this migration track:

- runtime surface inventory lives in `server/adapters/mcp/platform/runtime_inventory.py`
- router safety / semantic metadata lives in `server/router/infrastructure/tools_metadata/**`
- later discovery and public-surface shaping work must extend the platform-owned inventory rather than redefining it elsewhere
