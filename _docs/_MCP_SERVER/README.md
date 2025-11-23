# MCP Server Documentation

Documentation for the MCP Server (Client Side).

## 📚 Topic Index

- **[Clean Architecture](./clean_architecture.md)**
  - Detailed description of layers and control flow (DI).
  - Dependency separation principles implemented in version 0.1.5.

## 🚀 Running (Docker)

The server can be run in a Docker container for environment isolation.

### 1. Build Image
```bash
docker build -t blender-ai-mcp .
```

### 2. Run
To allow the container server to connect to Blender on the host, configure the network properly.

**MacOS / Windows:**
```bash
docker run -i --rm -e BLENDER_RPC_HOST=host.docker.internal blender-ai-mcp
```

**Linux:**
```bash
docker run -i --rm --network host -e BLENDER_RPC_HOST=127.0.0.1 blender-ai-mcp
```

*(The `-i` flag is crucial for the interactive stdio communication used by MCP)*.

## 🛠 Available Tools

### Scene Tools
Managing objects at the scene level.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `list_objects` | *none* | Returns a list of all objects in the scene with their type and position. |
| `delete_object` | `name` (str) | Deletes the specified object. Returns error if object does not exist. |
| `clean_scene` | `keep_lights_and_cameras` (bool, default True) | Deletes objects from scene. If `True`, preserves cameras and lights. If `False`, cleans the project completely ("hard reset"). |
| `duplicate_object` | `name` (str), `translation` ([x,y,z]) | Duplicates an object and optionally moves it. |
| `set_active_object` | `name` (str) | Sets the active object (crucial for context-dependent operations). |
| `get_viewport` | `width` (int), `height` (int) | Returns a rendered image of the scene (OpenGL) for the AI to inspect. |

### Modeling Tools
Geometry creation and editing.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `create_primitive` | `primitive_type` (str), `size` (float), `location` ([x,y,z]), `rotation` ([x,y,z]) | Creates a simple 3D object (Cube, Sphere, Cylinder, Plane, Cone, Torus, Monkey). |
| `transform_object` | `name` (str), `location` (opt), `rotation` (opt), `scale` (opt) | Changes position, rotation, or scale of an existing object. |
| `add_modifier` | `name` (str), `modifier_type` (str), `properties` (dict) | Adds a modifier to an object (e.g., `SUBSURF`, `BEVEL`). |
| `apply_modifier` | `name` (str), `modifier_name` (str) | Applies a modifier, permanently changing the mesh geometry. |

## 🛠 Key Components

### Entry Point (`server/main.py`)
Minimalist entry point.

### Dependency Injection (`server/infrastructure/di.py`)
Set of "Providers" (factory functions). Injects configuration from `server/infrastructure/config.py`.

### Configuration (`server/infrastructure/config.py`)
Environment variable handling (e.g., Blender IP address).

### Application Handlers (`server/application/tool_handlers/`)
Concrete tool logic implementations.
- `scene_handler.py`: Scene operations.
- `modeling_handler.py`: Modeling operations.

### Interfaces (`server/domain/`)
Abstract definitions of system contracts.
- `interfaces/rpc.py`: Contract for RPC client.
- `tools/scene.py`: Contract for scene tools.
- `tools/modeling.py`: Contract for modeling tools.
