# Clean Architecture in MCP Server

The MCP server project is organized according to Clean Architecture principles to separate business logic (modeling tools) from frameworks (MCP, Sockets).

## Layers

### 1. Domain (`server/domain`)
**System Core.** Depends on no external libraries (except standard types and Pydantic for models). Defines **WHAT** the system can do, but not **HOW**.

- **Interfaces (`interfaces/`)**: Contracts for external services (e.g., `IRpcClient`).
- **Tools (`tools/`)**: Abstract tool definitions (e.g., `ISceneTool`, `IModelingTool`).
- **Models (`models/`)**: Data structures (DTOs), e.g., `RpcRequest`.

### 2. Application (`server/application`)
**Application Logic (Use Cases).** Implements interfaces from the Domain layer. Depends only on Domain.

- **Tool Handlers (`tool_handlers/`)**: Concrete classes (e.g., `SceneToolHandler`, `ModelingToolHandler`) that know how to use `IRpcClient` to perform a task defined in `ISceneTool`.

### 3. Adapters (`server/adapters`)
**Adapters to the outside world.** Convert data from external formats to internal ones and vice versa.

- **RPC (`rpc/`)**: Socket client implementation (`RpcClient`) that satisfies `IRpcClient` interface.
- **MCP (`mcp/`)**: Input Layer (Driver Adapter).
  - `server.py`: Defines `@mcp.tool`. Retrieves handlers from Infrastructure layer and delegates control to them. Uses `fastmcp.Context` for logging.

### 4. Infrastructure (`server/infrastructure`)
**Technical details and configuration.**
- `di.py`: **Dependency Injection Providers**. Factory functions (`get_scene_handler`, `get_modeling_handler`) that create the dependency graph.
- Configuration (environment variables).
- Logging.

## Control Flow
1. `main.py` -> calls `adapters.mcp.server.run()`.
2. `adapters.mcp.server` (Tool Function) -> calls `infrastructure.di.get_scene_handler()`.
3. `infrastructure.di` -> creates (or returns existing) `RpcClient` and injects it into a new `SceneToolHandler`.
4. `adapters.mcp.server` -> calls `SceneToolHandler.list_objects()`.
5. `SceneToolHandler` -> calls `IRpcClient.send_request()`.
6. `RpcClient` -> sends JSON via socket.