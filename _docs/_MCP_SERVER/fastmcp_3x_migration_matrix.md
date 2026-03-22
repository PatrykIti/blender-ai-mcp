# FastMCP 3.x Migration Matrix

Canonical migration matrix for `TASK-083-01`.

Use this document together with `server/adapters/mcp/platform/runtime_inventory.py` to keep the platform migration grounded in explicit coupling points instead of implicit runtime assumptions.

## Baseline Policy

- Python support for the migration series is `3.11+`
- FastMCP baseline for the migration series is `>=3.0,<4.0`
- FastMCP `>=3.1,<4.0` is a feature gate for Tool Search / BM25 (`TASK-084`) and Code Mode (`TASK-094`)

## Current Runtime To Target Runtime

| Current location | Current 2.x-style assumption | 3.x target state | Follow-up |
|---|---|---|---|
| `pyproject.toml` | Runtime policy is not aligned with the practical dependency baseline | One explicit Python/FastMCP baseline for the entire migration series | `TASK-083-01` |
| `server/adapters/mcp/instance.py` | One global `mcp = FastMCP(...)` instance is the runtime source of truth | Compatibility shim only; composition root builds servers explicitly | `TASK-083-02`, `TASK-083-03` |
| `server/adapters/mcp/server.py` | Startup imports `server.adapters.mcp.areas` for side-effect registration | `build_server(surface_profile=...)` composes providers and transforms without hidden side effects | `TASK-083-02`, `TASK-083-03` |
| `server/adapters/mcp/areas/__init__.py` | Flat import list defines the public MCP catalog | Reusable provider groups / registrars define the catalog | `TASK-083-02` |
| `server/adapters/mcp/areas/*.py` | Tool modules bind directly to one global singleton with `@mcp.tool()` | Tool definitions register against `LocalProvider` or explicit registrars | `TASK-083-02` |
| `server/adapters/mcp/context_utils.py` | Sync tools use an ad hoc `ctx.info()` bridge | Context/session behavior becomes part of the platform bridge | `TASK-083-05` |
| `server/adapters/mcp/router_helper.py` | Router behavior is wrapped inside tool functions | Deterministic platform transform order owns router-aware shaping and execution semantics | `TASK-083-04`, `TASK-095`, `TASK-096`, `TASK-097` |
| `server/router/adapters/mcp_integration.py` | Router middleware assumes a flat public tool catalog | Router integration aligns with provider/factory composition and structured execution reporting | `TASK-083-04`, `TASK-089` |
| `server/router/infrastructure/metadata_loader.py` | Router metadata coverage is partial and implicit | Platform/runtime inventory and router metadata coverage gaps stay explicit | `TASK-083-01`, `TASK-084`, `TASK-086` |

## Known Inventory Gaps Captured By The Audit

| Gap | Current state | Why it matters |
|---|---|---|
| Side-effect bootstrap gap | `server.adapters.mcp.areas.__init__` does not import `text` | Hidden registration assumptions are already drifting from the actual MCP surface |
| Metadata loader gap | `MetadataLoader.AREAS` omits `armature`, `extraction`, and `text` despite metadata directories existing on disk | Router metadata and MCP exposure are already out of sync |
| Legacy Context import | `server/adapters/mcp/areas/armature.py` still imports `Context` from `mcp.server.fastmcp` | This is a direct FastMCP-era coupling that must be normalized before provider/factory work stabilizes |
| Flat catalog assumption | Nearly every area module imports `server.adapters.mcp.instance.mcp` directly | This blocks reusable providers and multi-surface composition |

## Source Of Truth

For this migration track:

- runtime surface inventory lives in `server/adapters/mcp/platform/runtime_inventory.py`
- router safety / semantic metadata lives in `server/router/infrastructure/tools_metadata/**`
- later discovery and public-surface shaping work must extend the platform-owned inventory rather than redefining it elsewhere
