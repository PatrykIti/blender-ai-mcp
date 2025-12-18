# TASK-045: Object Inspection Tools

**Priority:** 🟡 Medium
**Category:** Scene/Material Tools (Extensions)
**Estimated Effort:** Medium
**Dependencies:** TASK-043 (Scene Utility Tools), TASK-044 (Extraction Analysis Tools)
**Status:** ✅ **Done** (2025-12-04)

---

## Overview

Enhanced object inspection tools for deeper analysis of 3D objects. These tools provide access to metadata, hierarchy, spatial information, and material node graphs that are essential for understanding and documenting complex models.

**Use Cases:**
- Adding descriptive metadata/comments to objects (Custom Properties)
- Understanding object relationships and parent-child hierarchies
- Precise spatial analysis with bounding box corners
- Object pivot/origin analysis for transformation planning
- Material shader network inspection for procedural material understanding

**Tools Distribution:**
- `scene_*` tools: Custom Properties, Hierarchy, Bounding Box, Origin Info
- `material_*` tools: Material Nodes Inspector

---

## Architecture

```
server/domain/tools/
├── scene.py                       # ADD: new abstract methods
├── material.py                    # ADD: new abstract method

server/application/tool_handlers/
├── scene_handler.py               # ADD: new handler methods
├── material_handler.py            # ADD: new handler method

server/adapters/mcp/areas/
├── scene.py                       # ADD: 4 new MCP tools
├── material.py                    # ADD: 1 new MCP tool

blender_addon/application/handlers/
├── scene.py                       # ADD: 4 new Blender handlers
├── material.py                    # ADD: 1 new Blender handler
```

---

## Sub-Tasks

### TASK-045-1: scene_get_custom_properties

**Status:** ✅ Done

Read-only access to object custom properties (Blender's metadata system).

```python
@mcp.tool()
def scene_get_custom_properties(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets custom properties (metadata) from an object.

    Workflow: READ-ONLY | USE FOR → understanding object annotations/metadata

    Custom properties are key-value pairs stored on Blender objects.
    They can contain strings, numbers, arrays, or nested data.
    Useful for: object descriptions, export tags, rig parameters, game properties.

    Args:
        object_name: Name of the object to query

    Returns:
        JSON with custom properties:
        {
            "object_name": "Phone_Screen",
            "properties": {
                "description": "Main display panel",
                "export_group": "display",
                "lod_level": 0
            },
            "property_count": 3
        }
    """
```

**Blender API:**
```python
obj = bpy.data.objects.get(object_name)

# Get custom properties (excluding Blender internals starting with '_')
custom_props = {}
for key in obj.keys():
    if not key.startswith('_'):
        value = obj[key]
        # Handle IDPropertyGroup, arrays, etc.
        if hasattr(value, 'to_dict'):
            custom_props[key] = value.to_dict()
        elif hasattr(value, 'to_list'):
            custom_props[key] = value.to_list()
        else:
            custom_props[key] = value
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def get_custom_properties(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def get_custom_properties(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_get_custom_properties(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def get_custom_properties(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.get_custom_properties` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_get_custom_properties.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_get_custom_properties.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_get_custom_properties.py` | Full integration tests |

---

### TASK-045-2: scene_set_custom_property

**Status:** ✅ Done

Write custom properties (metadata) to objects.

```python
@mcp.tool()
def scene_set_custom_property(
    ctx: Context,
    object_name: str,
    property_name: str,
    property_value: str | int | float | bool,
    delete: bool = False
) -> str:
    """
    [OBJECT MODE][NON-DESTRUCTIVE] Sets or deletes a custom property on an object.

    Workflow: AFTER → scene_get_custom_properties | USE FOR → annotating objects

    Custom properties are preserved through file saves and exports (GLB, FBX).
    Use for: descriptions, comments, export tags, game properties.

    Args:
        object_name: Name of the object to modify
        property_name: Name of the custom property
        property_value: Value to set (string, int, float, or bool)
        delete: If True, removes the property instead of setting it

    Returns:
        Success message with property details:
        "Set custom property 'description' = 'Main display panel' on 'Phone_Screen'"
    """
```

**Blender API:**
```python
obj = bpy.data.objects.get(object_name)

if delete:
    if property_name in obj:
        del obj[property_name]
        return f"Deleted custom property '{property_name}' from '{object_name}'"
    else:
        return f"Property '{property_name}' not found on '{object_name}'"
else:
    obj[property_name] = property_value
    # For UI visibility, update property RNA
    if hasattr(obj, 'id_properties_ui'):
        ui = obj.id_properties_ui(property_name)
        ui.update(description=f"Custom property: {property_name}")
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def set_custom_property(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def set_custom_property(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_set_custom_property(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def set_custom_property(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.set_custom_property` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_set_custom_property.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_set_custom_property.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_set_custom_property.py` | Full integration tests |

---

### TASK-045-3: scene_get_hierarchy

**Status:** ✅ Done

Get parent-child hierarchy information for objects.

```python
@mcp.tool()
def scene_get_hierarchy(
    ctx: Context,
    object_name: str | None = None,
    include_transforms: bool = False
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets parent-child hierarchy for objects.

    Workflow: READ-ONLY | USE FOR → understanding object relationships

    If object_name is provided, returns hierarchy for that object (parents + children).
    If object_name is None, returns full scene hierarchy tree.

    Args:
        object_name: Specific object to query (None for full scene)
        include_transforms: Include local/world transform offsets

    Returns:
        JSON with hierarchy:
        {
            "object": "Phone_Body",
            "parent": "Phone_Root",
            "children": ["Phone_Screen", "Phone_Buttons", "Phone_Battery_Cover"],
            "depth": 2,
            "hierarchy_path": "Phone_Root > Phone_Body"
        }

        Or for full scene (object_name=None):
        {
            "roots": [
                {
                    "name": "Phone_Root",
                    "children": [
                        {"name": "Phone_Body", "children": [...]},
                        {"name": "Phone_Antenna", "children": []}
                    ]
                }
            ],
            "total_objects": 15,
            "max_depth": 3
        }
    """
```

**Blender API:**
```python
def get_hierarchy_tree(obj, include_transforms=False):
    result = {"name": obj.name, "children": []}
    if include_transforms:
        result["local_location"] = list(obj.location)
        result["local_rotation"] = list(obj.rotation_euler)
        result["local_scale"] = list(obj.scale)
    for child in obj.children:
        result["children"].append(get_hierarchy_tree(child, include_transforms))
    return result

# Find root objects (no parent)
roots = [obj for obj in bpy.data.objects if obj.parent is None]

# Build hierarchy tree
hierarchy = {"roots": [get_hierarchy_tree(r) for r in roots]}
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def get_hierarchy(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def get_hierarchy(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_get_hierarchy(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def get_hierarchy(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.get_hierarchy` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_get_hierarchy.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_get_hierarchy.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_get_hierarchy.py` | Full integration tests |

---

### TASK-045-4: scene_get_bounding_box

**Status:** ✅ Done

Get precise bounding box corners for objects.

```python
@mcp.tool()
def scene_get_bounding_box(
    ctx: Context,
    object_name: str,
    world_space: bool = True
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets bounding box corners for an object.

    Workflow: READ-ONLY | USE FOR → spatial analysis, collision detection planning

    Returns all 8 corners of the axis-aligned bounding box plus center and dimensions.

    Args:
        object_name: Name of the object to query
        world_space: If True, returns world coordinates. If False, local coordinates.

    Returns:
        JSON with bounding box data:
        {
            "object_name": "Phone_Body",
            "space": "world",
            "min": [-0.5, -1.0, 0.0],
            "max": [0.5, 1.0, 0.2],
            "center": [0.0, 0.0, 0.1],
            "dimensions": [1.0, 2.0, 0.2],
            "corners": [
                [-0.5, -1.0, 0.0],  # min corner
                [-0.5, -1.0, 0.2],
                [-0.5, 1.0, 0.0],
                [-0.5, 1.0, 0.2],
                [0.5, -1.0, 0.0],
                [0.5, -1.0, 0.2],
                [0.5, 1.0, 0.0],
                [0.5, 1.0, 0.2]   # max corner
            ],
            "volume": 0.4
        }
    """
```

**Blender API:**
```python
obj = bpy.data.objects.get(object_name)

if world_space:
    # Get world-space bounding box
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
else:
    # Local space
    corners = [Vector(corner) for corner in obj.bound_box]

# Calculate min/max
min_corner = Vector((
    min(c.x for c in corners),
    min(c.y for c in corners),
    min(c.z for c in corners)
))
max_corner = Vector((
    max(c.x for c in corners),
    max(c.y for c in corners),
    max(c.z for c in corners)
))

center = (min_corner + max_corner) / 2
dimensions = max_corner - min_corner
volume = dimensions.x * dimensions.y * dimensions.z
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def get_bounding_box(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def get_bounding_box(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_get_bounding_box(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def get_bounding_box(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.get_bounding_box` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_get_bounding_box.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_get_bounding_box.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_get_bounding_box.py` | Full integration tests |

---

### TASK-045-5: scene_get_origin_info

**Status:** ✅ Done

Get object origin/pivot point information.

```python
@mcp.tool()
def scene_get_origin_info(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Gets origin (pivot point) information for an object.

    Workflow: READ-ONLY | USE FOR → transformation planning, origin adjustment decisions

    Returns origin location relative to geometry and bounding box.
    Helps determine if origin should be moved (e.g., to center, to bottom, to cursor).

    Args:
        object_name: Name of the object to query

    Returns:
        JSON with origin information:
        {
            "object_name": "Phone_Body",
            "origin_world": [0.0, 0.0, 0.0],
            "origin_local": [0.0, 0.0, 0.0],
            "relative_to_bbox": {
                "x": 0.5,  # 0=min, 0.5=center, 1=max
                "y": 0.5,
                "z": 0.0   # Origin at bottom
            },
            "relative_to_geometry_center": [0.0, 0.0, -0.1],
            "suggestions": [
                "Origin is at bottom center - good for floor placement",
                "Use 'ORIGIN_GEOMETRY' to center on mesh"
            ]
        }
    """
```

**Blender API:**
```python
obj = bpy.data.objects.get(object_name)

# Origin in world space
origin_world = obj.matrix_world.translation.copy()

# Origin in local space (always 0,0,0 but useful for reference)
origin_local = Vector((0, 0, 0))

# Get bounding box for relative position
corners = [Vector(c) for c in obj.bound_box]
min_corner = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
max_corner = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
bbox_size = max_corner - min_corner

# Relative position (0=min, 0.5=center, 1=max)
relative = Vector((
    (0 - min_corner.x) / bbox_size.x if bbox_size.x != 0 else 0.5,
    (0 - min_corner.y) / bbox_size.y if bbox_size.y != 0 else 0.5,
    (0 - min_corner.z) / bbox_size.z if bbox_size.z != 0 else 0.5,
))

# Geometry center (average of all vertices)
if obj.type == 'MESH':
    verts = obj.data.vertices
    if verts:
        geo_center = sum((v.co for v in verts), Vector()) / len(verts)
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def get_origin_info(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def get_origin_info(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_get_origin_info(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def get_origin_info(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.get_origin_info` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_get_origin_info.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_get_origin_info.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_get_origin_info.py` | Full integration tests |

---

### TASK-045-6: material_inspect_nodes

**Status:** ✅ Done

Inspect material shader node graph.

```python
@mcp.tool()
def material_inspect_nodes(
    ctx: Context,
    material_name: str,
    include_connections: bool = True
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Inspects material shader node graph.

    Workflow: READ-ONLY | USE FOR → understanding procedural materials, debugging shaders

    Returns all nodes in the material's node tree with their types,
    parameters, and connections.

    Args:
        material_name: Name of the material to inspect
        include_connections: Include node connections/links (default True)

    Returns:
        JSON with node graph:
        {
            "material_name": "Phone_Screen_Material",
            "use_nodes": true,
            "node_count": 5,
            "nodes": [
                {
                    "name": "Principled BSDF",
                    "type": "BSDF_PRINCIPLED",
                    "location": [0, 0],
                    "inputs": {
                        "Base Color": {"value": [0.1, 0.1, 0.1, 1.0], "connected": true},
                        "Metallic": {"value": 0.0, "connected": false},
                        "Roughness": {"value": 0.1, "connected": false}
                    }
                },
                {
                    "name": "Image Texture",
                    "type": "TEX_IMAGE",
                    "location": [-300, 0],
                    "image": "screen_diffuse.png",
                    "color_space": "sRGB"
                }
            ],
            "connections": [
                {"from": "Image Texture.Color", "to": "Principled BSDF.Base Color"}
            ],
            "output_node": "Material Output"
        }
    """
```

**Blender API:**
```python
mat = bpy.data.materials.get(material_name)

if not mat.use_nodes:
    return {"material_name": material_name, "use_nodes": False}

node_tree = mat.node_tree
nodes = []

for node in node_tree.nodes:
    node_data = {
        "name": node.name,
        "type": node.type,
        "location": list(node.location),
    }

    # Get input values
    inputs = {}
    for inp in node.inputs:
        input_data = {"connected": inp.is_linked}
        if hasattr(inp, 'default_value'):
            val = inp.default_value
            if hasattr(val, '__iter__'):
                input_data["value"] = list(val)
            else:
                input_data["value"] = val
        inputs[inp.name] = input_data
    node_data["inputs"] = inputs

    # Special handling for specific node types
    if node.type == 'TEX_IMAGE' and node.image:
        node_data["image"] = node.image.name
        node_data["color_space"] = node.image.colorspace_settings.name

    nodes.append(node_data)

# Get connections
connections = []
for link in node_tree.links:
    connections.append({
        "from": f"{link.from_node.name}.{link.from_socket.name}",
        "to": f"{link.to_node.name}.{link.to_socket.name}"
    })
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/material.py` | `@abstractmethod def inspect_nodes(...)` |
| Application | `server/application/tool_handlers/material_handler.py` | `def inspect_nodes(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/material.py` | `@mcp.tool() def material_inspect_nodes(...)` |
| Addon | `blender_addon/application/handlers/material.py` | `def inspect_nodes(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `material.inspect_nodes` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` |
| Router Metadata | `server/router/infrastructure/tools_metadata/material/material_inspect_nodes.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/material/test_inspect_nodes.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/material/test_inspect_nodes.py` | Full integration tests |

---

## Testing Requirements

- [ ] Unit tests for each tool handler
- [ ] E2E tests for each tool with Blender integration
- [ ] E2E test: Custom properties round-trip (set → get → verify)
- [ ] E2E test: Hierarchy inspection on parent-child model
- [ ] E2E test: Bounding box accuracy verification
- [ ] E2E test: Material node inspection on procedural material

---

## Implementation Order

Recommended implementation order based on dependencies:

1. **scene_get_custom_properties** (foundation - read-only, simple)
2. **scene_set_custom_property** (depends on understanding custom props)
3. **scene_get_bounding_box** (independent, commonly needed)
4. **scene_get_origin_info** (uses bounding box concepts)
5. **scene_get_hierarchy** (independent, useful for complex models)
6. **material_inspect_nodes** (independent, different area)

---

## New Files to Create

### Server Side
```
server/router/infrastructure/tools_metadata/scene/
  ├── scene_get_custom_properties.json
  ├── scene_set_custom_property.json
  ├── scene_get_hierarchy.json
  ├── scene_get_bounding_box.json
  └── scene_get_origin_info.json

server/router/infrastructure/tools_metadata/material/
  └── material_inspect_nodes.json
```

### Tests
```
tests/unit/tools/scene/
  ├── test_get_custom_properties.py
  ├── test_set_custom_property.py
  ├── test_get_hierarchy.py
  ├── test_get_bounding_box.py
  └── test_get_origin_info.py

tests/unit/tools/material/
  └── test_inspect_nodes.py

tests/e2e/tools/scene/
  ├── test_get_custom_properties.py
  ├── test_set_custom_property.py
  ├── test_get_hierarchy.py
  ├── test_get_bounding_box.py
  └── test_get_origin_info.py

tests/e2e/tools/material/
  └── test_inspect_nodes.py
```

---

## Documentation Updates Required

After implementing these tools, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-045_Object_Inspection_Tools.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Add TASK-045 to task list, update statistics |
| `_docs/_CHANGELOG/{NN}-{date}-object-inspection-tools.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add new tools to scene/material tables |
| `_docs/_ADDON/README.md` | Add RPC commands to handler tables |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add tools with arguments |
| `_docs/SCENE_TOOLS_ARCHITECTURE.md` | Add scene inspection tools documentation |
| `_docs/MATERIAL_TOOLS_ARCHITECTURE.md` | Add material inspection tool documentation |
| `README.md` | Update roadmap, add to autoApprove lists |

---

## Router Integration

### Example: scene_get_custom_properties.json

```json
{
  "tool_name": "scene_get_custom_properties",
  "category": "scene",
  "mode_required": "OBJECT",
  "selection_required": false,
  "keywords": ["custom properties", "metadata", "annotations", "tags", "description", "comments"],
  "sample_prompts": [
    "what custom properties does this object have",
    "get object metadata",
    "show object annotations"
  ],
  "parameters": {
    "object_name": {"type": "string", "required": true, "description": "Object to query"}
  },
  "related_tools": ["scene_set_custom_property", "scene_inspect"],
  "patterns": [],
  "description": "Gets custom properties (metadata) from an object."
}
```

### Example: material_inspect_nodes.json

```json
{
  "tool_name": "material_inspect_nodes",
  "category": "material",
  "mode_required": "OBJECT",
  "selection_required": false,
  "keywords": ["material", "shader", "nodes", "node graph", "texture", "procedural"],
  "sample_prompts": [
    "show material node graph",
    "what nodes does this material use",
    "inspect shader setup"
  ],
  "parameters": {
    "material_name": {"type": "string", "required": true, "description": "Material to inspect"},
    "include_connections": {"type": "boolean", "required": false, "default": true}
  },
  "related_tools": ["material_list", "material_create", "material_set_texture"],
  "patterns": [],
  "description": "Inspects material shader node graph."
}
```

---

## Relation to Other Tasks

TASK-045 extends the inspection capabilities started in TASK-043 and TASK-044:

```
TASK-043 (Scene Utility Tools) → TASK-045 (Object Inspection - deeper analysis)
TASK-044 (Extraction Tools) → TASK-045 (Additional inspection for workflow extraction)
```

These tools complement the extraction workflow by providing:
- Metadata storage for extracted workflow annotations
- Hierarchy understanding for complex multi-part models
- Precise spatial data for programmatic transformations
- Material understanding for texture/shader extraction
