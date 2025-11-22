# 6. FastMCP DI Refactor

**Date:** 2025-11-22  
**Version:** 0.1.5  
**Tasks:** TASK-003_3_Refactor_FastMCP_Dependency_Injection

## 🚀 Key Changes

### Infrastructure Layer (`server/infrastructure/`)
- Replaced `container.py` (Global State) with `di.py` (Providers).
- Implemented factory functions (`get_rpc_client`, `get_scene_handler`) compliant with the Singleton pattern (module cache).

### Adapters Layer (`server/adapters/mcp/`)
- Removed global container import in `server.py`.
- MCP Tools now explicitly retrieve their dependencies (handlers) using providers from `di.py`.
- Added `Context` injection (from `fastmcp`) to tools, enabling structured logging (`ctx.info`, `ctx.error`).

This change eliminates the "magical" global container variable in the adapter layer and paves the way for more advanced DI in the future (e.g., `Depends` in FastMCP).