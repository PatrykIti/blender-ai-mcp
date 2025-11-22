# Blender Addon Documentation

Documentation for the Blender Addon (Server Side).

## 📚 Topic Index

- **[RPC Architecture and Threading](./rpc_architecture.md)**
  - Explanation of the multi-threaded model.
  - `bpy.app.timers` mechanism.
  - JSON Protocol.

## 🛠 Structure (Clean Architecture)

The Addon is layered to separate Blender logic from networking mechanisms.

### 1. Entry Point (`__init__.py`)
The main entry point. Responsible for:
- Registration in Blender (`bl_info`).
- Instantiating Application Handlers.
- Registering Handlers in the RPC Server.
- Starting the server in a separate thread.

### 2. Application (`application/handlers/`)
Business Logic ("How to do it in Blender").
- `scene.py`: `SceneHandler` (List objects, delete).
- `modeling.py`: `ModelingHandler` (Create primitives, transforms, modifiers).
- Direct usage of `bpy`.

### 3. Infrastructure (`infrastructure/`)
Technical details.
- `rpc_server.py`: TCP Server implementation. It knows nothing about business logic, only accepts JSON requests and dispatches them to registered callbacks.

## 🛠 Available API Commands

### Scene (`application/handlers/scene.py`)
| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `scene.list_objects` | `list_objects` | Lists objects in the scene. |
| `scene.delete_object` | `delete_object` | Deletes an object. |
| `scene.clean_scene` | `clean_scene` | Clears the scene. |

### Modeling (`application/handlers/modeling.py`)
| RPC Command | Handler Method | Description |
|-------------|----------------|-------------|
| `modeling.create_primitive` | `create_primitive` | Creates a primitive (Cube, Sphere, etc.). |
| `modeling.transform_object` | `transform_object` | Moves, rotates, or scales an object. |
| `modeling.add_modifier` | `add_modifier` | Adds a modifier to an object. |