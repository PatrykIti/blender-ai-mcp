# Clean Architecture in MCP Server

The MCP server project is organized according to Clean Architecture principles to separate business logic (modeling tools) from frameworks (MCP, Sockets).

## Layers

### 1. Domain (`server/domain`)
**System Core.** Depends on no external libraries (except standard types and Pydantic for models). Defines **WHAT** the system can do, but not **HOW**.

- **Interfaces (`interfaces/`)**: Contracts for external services (e.g., `IRpcClient`).
- **Tools (`tools/`)**: Abstract tool definitions:
  - `ISceneTool` - Scene operations (list, delete, inspect, viewport)
  - `IModelingTool` - Object Mode modeling (primitives, transforms, modifiers)
  - `IMeshTool` - Edit Mode mesh operations (extrude, bevel, select, etc.)
  - `ICurveTool` - Curve operations (create, convert to mesh)
  - `ICollectionTool` - Collection management
  - `IMaterialTool` - Material operations
  - `IUVTool` - UV mapping operations
- **Models (`models/`)**: Data structures (DTOs), e.g., `RpcRequest`.

### 2. Application (`server/application`)
**Application Logic (Use Cases).** Implements interfaces from the Domain layer. Depends only on Domain.

- **Tool Handlers (`tool_handlers/`)**: Concrete classes that use `IRpcClient` to perform tasks:
  - `SceneToolHandler` implements `ISceneTool`
  - `ModelingToolHandler` implements `IModelingTool`
  - `MeshToolHandler` implements `IMeshTool`
  - `CurveToolHandler` implements `ICurveTool`
  - `CollectionToolHandler` implements `ICollectionTool`
  - `MaterialToolHandler` implements `IMaterialTool`
  - `UVToolHandler` implements `IUVTool`

### 3. Adapters (`server/adapters`)
**Adapters to the outside world.** Convert data from external formats to internal ones and vice versa.

- **RPC (`rpc/`)**: Socket client implementation (`RpcClient`) that satisfies `IRpcClient` interface.
- **MCP (`mcp/`)**: Input Layer (Driver Adapter).
  - `instance.py`: Initializes the shared `FastMCP` application instance.
  - `areas/`: Modular definitions of tools. Each file imports `mcp` from `instance.py` and defines `@mcp.tool` functions that delegate to Application Handlers:
    - `scene.py` - Scene tools (list, delete, inspect, context, create, viewport)
    - `modeling.py` - Modeling tools (primitives, transforms, modifiers)
    - `mesh.py` - Mesh Edit Mode tools (extrude, bevel, select, bridge, spin, etc.)
    - `curve.py` - Curve tools (create, convert to mesh)
    - `collection.py` - Collection tools (list, list_objects)
    - `material.py` - Material tools (list, list_by_object)
    - `uv.py` - UV tools (list_maps)
  - `server.py`: Entry point that imports areas (triggering registration) and exposes the `run()` function.

### 4. Infrastructure (`server/infrastructure`)
**Technical details and configuration.**
- `di.py`: **Dependency Injection Providers**. Factory functions that create the dependency graph:
  - `get_rpc_client()` - Returns singleton RPC client
  - `get_scene_handler()` - Creates SceneToolHandler
  - `get_modeling_handler()` - Creates ModelingToolHandler
  - `get_mesh_handler()` - Creates MeshToolHandler
  - `get_curve_handler()` - Creates CurveToolHandler
  - `get_collection_handler()` - Creates CollectionToolHandler
  - `get_material_handler()` - Creates MaterialToolHandler
  - `get_uv_handler()` - Creates UVToolHandler
- Configuration (environment variables).
- Logging.

## Control Flow

Example: Calling `scene_list_objects` tool

1. `main.py` -> calls `adapters.mcp.server.run()`.
2. `adapters.mcp.areas.scene` (Tool Function) -> calls `infrastructure.di.get_scene_handler()`.
3. `infrastructure.di` -> creates (or returns cached) `RpcClient` and injects it into `SceneToolHandler`.
4. `adapters.mcp.areas.scene` -> calls `SceneToolHandler.list_objects()`.
5. `SceneToolHandler` -> calls `IRpcClient.send_request("list_objects", ...)`.
6. `RpcClient` -> sends JSON via socket to Blender Addon.
7. Blender Addon -> processes request, returns JSON response.
8. `RpcClient` -> receives response, returns to handler.
9. `SceneToolHandler` -> formats result string for AI model.

This flow is identical for all tool areas (mesh, curve, modeling, etc.) - only the handler and RPC command names differ.
