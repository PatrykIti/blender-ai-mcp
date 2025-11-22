# 5. Main and DI Refactor

**Date:** 2025-11-22  
**Version:** 0.1.4  
**Tasks:** TASK-003_2_Refactor_Main_DI

## 🚀 Key Changes

### Infrastructure (Dependency Injection)
- Added `server/infrastructure/container.py`: DI Container that builds the dependency graph (creates `RpcClient` and injects it into `SceneToolHandler`).

### Adapters (MCP)
- Moved MCP tool definitions to `server/adapters/mcp/server.py`. Tools now use handler instances provided by the DI container.

### Entry Point
- The `server/main.py` file has been maximally simplified. It now only serves to start the server defined in adapters.

This change completes the process of adapting the code to **Clean Architecture**. The architecture is now fully modular and ready for adding new tools (TASK-004).