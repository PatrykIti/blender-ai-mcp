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

| `list_objects` | `list_objects` | Lists objects in the scene. |

| `delete_object` | `delete_object` | Deletes an object. |

| `clean_scene` | `clean_scene` | Clears the scene. |

| `duplicate_object` | `duplicate_object` | Duplicates an object and optionally moves it. |

| `set_active_object` | `set_active_object` | Sets the active object. |

| `get_viewport` | `get_viewport` | Returns a base64 encoded OpenGL render. Supports `shading`, `camera_name`, and `focus_target`. |



### Modeling (`application/handlers/modeling.py`)



| RPC Command | Handler Method | Description |



|-------------|----------------|-------------|



| `create_primitive` | `create_primitive` | Creates a primitive (Cube, Sphere, etc.). |



| `transform_object` | `transform_object` | Moves, rotates, or scales an object. |



| `add_modifier` | `add_modifier` | Adds a modifier to an object. |



| `apply_modifier` | `apply_modifier` | Applies (finalizes) a modifier on an object. |



| `convert_to_mesh` | `convert_to_mesh` | Converts a non-mesh object to a mesh. |



| `join_objects` | `join_objects` | Joins multiple mesh objects into one. |



| `separate_object` | `separate_object` | Separates a mesh object into new objects. |



| `set_origin` | `set_origin` | Sets the origin point of an object. |

| `get_modifiers` | `get_modifiers` | Returns a list of modifiers on the object. |


### Mesh (`application/handlers/mesh.py`)

| RPC Command | Handler Method | Description |

|-------------|----------------|-------------|

| `select_all` | `select_all` | Selects or deselects all geometry elements. |

| `delete_selected` | `delete_selected` | Deletes selected elements (VERT, EDGE, FACE). |

| `select_by_index` | `select_by_index` | Selects elements by index using BMesh. |

| `extrude_region` | `extrude_region` | Extrudes selected region (optionally moves). |

| `fill_holes` | `fill_holes` | Fills holes by creating faces. |


