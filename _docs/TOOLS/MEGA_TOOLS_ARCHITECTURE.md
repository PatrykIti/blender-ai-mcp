# Mega Tools Architecture

Mega tools are unified tools that consolidate multiple related operations to **reduce LLM context usage**.
They are wrappers only: standalone action handlers still exist and are the source of truth for execution.

**Implementation pattern (see `scene_context`):**
- Mega tool is exposed as a single `@mcp.tool`.
- Action-level functions are **internal** (no `@mcp.tool`) and call Blender addon RPC handlers.
- If a standalone MCP tool is required for workflow compatibility, it should be a thin wrapper
  that calls the same internal action function (no duplicated logic).
- Router can still execute internal actions directly via handler mappings and per-tool JSON metadata.

---

## 🧠 LLM Context Optimization

| Mega Tool | Actions | Replaces | Savings |
|-----------|---------|----------|---------|
| `scene_context` | `mode`, `selection` | `scene_get_mode`, `scene_list_selection` | -1 |
| `scene_create` | `light`, `camera`, `empty` | `scene_create_light`, `scene_create_camera`, `scene_create_empty` | -2 |
| `scene_inspect` | `object`, `topology`, `modifiers`, `materials`, `constraints`, `modifier_data` | `scene_inspect_object`, `scene_inspect_mesh_topology`, `scene_inspect_modifiers`, `scene_inspect_material_slots`, `scene_get_constraints`, `modeling_get_modifier_data` | -5 |
| `mesh_select` | `all`, `none`, `linked`, `more`, `less`, `boundary` | `mesh_select_all`, `mesh_select_linked`, `mesh_select_more`, `mesh_select_less`, `mesh_select_boundary` | -4 |
| `mesh_select_targeted` | `by_index`, `loop`, `ring`, `by_location` | `mesh_select_by_index`, `mesh_select_loop`, `mesh_select_ring`, `mesh_select_by_location` | -3 |
| `mesh_inspect` | `vertices`, `edges`, `faces`, `uvs`, `normals`, `attributes`, `shape_keys`, `group_weights`, `summary` | `mesh_get_*` introspection tools | -7 |

**Total:** 28 tools → 6 mega tools (**-22 definitions** for LLM context)

**`mesh_inspect.summary` sources (recommended):**
- `scene_inspect(action="topology")` → counts
- `uv_list_maps` → `has_uvs`
- `mesh_get_shape_keys` → `has_shape_keys`
- `mesh_get_loop_normals` or mesh flags → `has_custom_normals`
- `mesh_list_groups` → `vertex_groups`
- `modeling_list_modifiers` → `modifiers`

---

# 1. scene_context ✅ Done

Quick context queries for scene state.

**Tag:** `[SCENE][READ-ONLY][SAFE]`

## Actions

| Action | Description |
|--------|-------------|
| `"mode"` | Returns current Blender mode, active object, selection count. |
| `"selection"` | Returns selected objects list + edit mode vertex/edge/face counts. |

## Examples

```json
{
  "tool": "scene_context",
  "args": {
    "action": "mode"
  }
}
```

```json
{
  "tool": "scene_context",
  "args": {
    "action": "selection"
  }
}
```

## Replaces

- `scene_get_mode` → `scene_context(action="mode")`
- `scene_list_selection` → `scene_context(action="selection")`

---

# 2. scene_create ✅ Done

Creates scene helper objects (lights, cameras, empties).

**Tag:** `[SCENE][SAFE]`

## Actions

| Action | Parameters | Description |
|--------|------------|-------------|
| `"light"` | `light_type`, `energy`, `color`, `location`, `name` | Creates light source (POINT/SUN/SPOT/AREA). |
| `"camera"` | `location`, `rotation`, `lens`, `clip_start`, `clip_end`, `name` | Creates camera object. |
| `"empty"` | `empty_type`, `size`, `location`, `name` | Creates empty object (PLAIN_AXES/ARROWS/CUBE/etc.). |

## Light Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `light_type` | `Literal["POINT", "SUN", "SPOT", "AREA"]` | `"POINT"` | Type of light source. |
| `energy` | `float` | `1000.0` | Power in Watts. |
| `color` | `List[float]` or `str` | `[1.0, 1.0, 1.0]` | RGB color (0.0 to 1.0). |
| `location` | `List[float]` or `str` | `[0.0, 0.0, 0.0]` | [x, y, z] position. |
| `name` | `str` | `None` | Optional custom name. |

## Camera Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location` | `List[float]` or `str` | `[0.0, 0.0, 0.0]` | [x, y, z] position. |
| `rotation` | `List[float]` or `str` | `[0.0, 0.0, 0.0]` | Euler angles in radians. |
| `lens` | `float` | `50.0` | Focal length in mm. |
| `clip_start` | `float` | `None` | Near clipping distance. |
| `clip_end` | `float` | `None` | Far clipping distance. |
| `name` | `str` | `None` | Optional custom name. |

## Empty Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `empty_type` | `Literal[...]` | `"PLAIN_AXES"` | Display type (PLAIN_AXES/ARROWS/CIRCLE/CUBE/SPHERE/CONE/IMAGE). |
| `size` | `float` | `1.0` | Display size. |
| `location` | `List[float]` or `str` | `[0.0, 0.0, 0.0]` | [x, y, z] position. |
| `name` | `str` | `None` | Optional custom name. |

## Examples

```json
{
  "tool": "scene_create",
  "args": {
    "action": "light",
    "light_type": "SUN",
    "energy": 5.0,
    "location": [0, 0, 5]
  }
}
```

```json
{
  "tool": "scene_create",
  "args": {
    "action": "camera",
    "location": [0, -10, 5],
    "rotation": [1.0, 0, 0],
    "lens": 85.0
  }
}
```

```json
{
  "tool": "scene_create",
  "args": {
    "action": "empty",
    "empty_type": "ARROWS",
    "location": [0, 0, 2]
  }
}
```

## Replaces

- `scene_create_light` → `scene_create(action="light", ...)`
- `scene_create_camera` → `scene_create(action="camera", ...)`
- `scene_create_empty` → `scene_create(action="empty", ...)`

---

# 3. scene_inspect ✅ Done

Detailed inspection queries for objects and scene.

**Tag:** `[SCENE][READ-ONLY][SAFE]`

## Actions

| Action | Parameters | Description |
|--------|------------|-------------|
| `"object"` | `object_name` (required) | Returns transform, collections, materials, modifiers, mesh stats for a single object. |
| `"topology"` | `object_name` (required), `detailed` | Returns vertex/edge/face/tri/quad/ngon counts. Optional: `detailed=True` for non-manifold checks. |
| `"modifiers"` | `object_name` (optional), `include_disabled` | Returns modifier stacks. If `object_name` is None, scans all objects. |
| `"materials"` | `material_filter`, `include_empty_slots` | Returns material slot audit across scene. |
| `"constraints"` | `object_name`, `include_bones` | Returns object (and optional bone) constraints. |
| `"modifier_data"` | `object_name`, `modifier_name`, `include_node_tree` | Returns full modifier properties. |

## Object Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | `str` | **required** | Name of the object to inspect. |

## Topology Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | `str` | **required** | Name of the mesh object to analyze. |
| `detailed` | `bool` | `False` | Include non-manifold/loose geometry checks. |

## Modifiers Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | `str` | `None` | Object name (None scans all objects). |
| `include_disabled` | `bool` | `True` | Include disabled modifiers in output. |

## Materials Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `material_filter` | `str` | `None` | Filter materials by name substring. |
| `include_empty_slots` | `bool` | `True` | Include empty material slots. |

## Constraints Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | `str` | **required** | Target object. |
| `include_bones` | `bool` | `False` | Include bone constraints (armatures). |

## Modifier Data Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | `str` | **required** | Target object. |
| `modifier_name` | `str` | `None` | Filter to a specific modifier. |
| `include_node_tree` | `bool` | `False` | Include Geometry Nodes group metadata. |

## Examples

```json
{
  "tool": "scene_inspect",
  "args": {
    "action": "object",
    "object_name": "Cube"
  }
}
```

```json
{
  "tool": "scene_inspect",
  "args": {
    "action": "topology",
    "object_name": "Cube",
    "detailed": true
  }
}
```

```json
{
  "tool": "scene_inspect",
  "args": {
    "action": "modifiers",
    "object_name": "Cube"
  }
}
```

```json
{
  "tool": "scene_inspect",
  "args": {
    "action": "modifiers"
  }
}
```

```json
{
  "tool": "scene_inspect",
  "args": {
    "action": "materials",
    "material_filter": "Wood"
  }
}
```

## Replaces

- `scene_inspect_object` → `scene_inspect(action="object", ...)`
- `scene_inspect_mesh_topology` → `scene_inspect(action="topology", ...)`
- `scene_inspect_modifiers` → `scene_inspect(action="modifiers", ...)`
- `scene_inspect_material_slots` → `scene_inspect(action="materials", ...)`
- `scene_get_constraints` → `scene_inspect(action="constraints", ...)`
- `modeling_get_modifier_data` → `scene_inspect(action="modifier_data", ...)`

---

# 4. mesh_select ✅ Done

Simple selection operations for mesh geometry.

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

**Tip:** For predictable results with selection-based `mesh_*` tools (extrude/bevel/etc.), make the selection explicitly with `mesh_select` / `mesh_select_targeted`. Router `auto_selection` only selects-all when the Edit Mode selection is empty and does not override an existing selection.

## Actions

| Action | Parameters | Description |
|--------|------------|-------------|
| `"all"` | *none* | Selects all geometry. |
| `"none"` | *none* | Deselects all geometry. |
| `"linked"` | *none* | Selects all geometry connected to current selection. |
| `"more"` | *none* | Grows selection by 1 step. |
| `"less"` | *none* | Shrinks selection by 1 step. |
| `"boundary"` | `boundary_mode` | Selects boundary edges/vertices. |

## Boundary Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `boundary_mode` | `Literal["EDGE", "VERT"]` | `"EDGE"` | Select boundary edges or vertices. |

## Examples

```json
{
  "tool": "mesh_select",
  "args": {
    "action": "all"
  }
}
```

```json
{
  "tool": "mesh_select",
  "args": {
    "action": "linked"
  }
}
```

```json
{
  "tool": "mesh_select",
  "args": {
    "action": "boundary",
    "boundary_mode": "EDGE"
  }
}
```

## Replaces

- `mesh_select_all(deselect=False)` → `mesh_select(action="all")`
- `mesh_select_all(deselect=True)` → `mesh_select(action="none")`
- `mesh_select_linked` → `mesh_select(action="linked")`
- `mesh_select_more` → `mesh_select(action="more")`
- `mesh_select_less` → `mesh_select(action="less")`
- `mesh_select_boundary` → `mesh_select(action="boundary")`

---

# 5. mesh_select_targeted ✅ Done

Targeted selection operations for mesh geometry (with parameters).

**Tag:** `[EDIT MODE][SELECTION-BASED][SAFE]`

## Actions

| Action | Required Parameters | Description |
|--------|---------------------|-------------|
| `"by_index"` | `indices` | Selects specific elements by index. |
| `"loop"` | `edge_index` | Selects edge loop from target edge. |
| `"ring"` | `edge_index` | Selects edge ring from target edge. |
| `"by_location"` | `axis`, `min_coord`, `max_coord` | Selects geometry within coordinate range. |

## By Index Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `indices` | `List[int]` | **required** | List of element indices to select. |
| `element_type` | `Literal["VERT", "EDGE", "FACE"]` | `"VERT"` | Type of elements to select. |
| `selection_mode` | `Literal["SET", "ADD", "SUBTRACT"]` | `"SET"` | Selection mode. |

## Loop/Ring Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `edge_index` | `int` | **required** | Index of the target edge. |

## By Location Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `axis` | `Literal["X", "Y", "Z"]` | **required** | Axis to evaluate. |
| `min_coord` | `float` | **required** | Minimum coordinate value (inclusive). |
| `max_coord` | `float` | **required** | Maximum coordinate value (inclusive). |
| `element_type` | `Literal["VERT", "EDGE", "FACE"]` | `"VERT"` | Type of elements to select. |

## Examples

```json
{
  "tool": "mesh_select_targeted",
  "args": {
    "action": "by_index",
    "indices": [0, 1, 2],
    "element_type": "VERT"
  }
}
```

```json
{
  "tool": "mesh_select_targeted",
  "args": {
    "action": "loop",
    "edge_index": 4
  }
}
```

```json
{
  "tool": "mesh_select_targeted",
  "args": {
    "action": "ring",
    "edge_index": 3
  }
}
```

```json
{
  "tool": "mesh_select_targeted",
  "args": {
    "action": "by_location",
    "axis": "Z",
    "min_coord": 0.5,
    "max_coord": 2.0
  }
}
```

## Replaces

- `mesh_select_by_index` → `mesh_select_targeted(action="by_index", ...)`
- `mesh_select_loop` → `mesh_select_targeted(action="loop", ...)`
- `mesh_select_ring` → `mesh_select_targeted(action="ring", ...)`
- `mesh_select_by_location` → `mesh_select_targeted(action="by_location", ...)`

---

# 6. mesh_inspect ✅ Done

Mesh introspection mega tool (summary + raw payloads).

**Tag:** `[MESH][READ-ONLY][SAFE]`

## Actions

| Action | Description |
|--------|-------------|
| `"summary"` | Lightweight overview (counts + presence flags). |
| `"vertices"` | Vertex positions + selection states. |
| `"edges"` | Edge connectivity + flags. |
| `"faces"` | Face connectivity + normals/material index. |
| `"uvs"` | UV loop coordinates. |
| `"normals"` | Per-loop normals (split/custom). |
| `"attributes"` | Mesh attributes (vertex colors/layers). |
| `"shape_keys"` | Shape key list + optional deltas. |
| `"group_weights"` | Vertex group weights. |

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_name` | `str` | **required** | Name of the object to inspect. |
| `selected_only` | `bool` | `False` | Only return selected elements (where applicable). |
| `uv_layer` | `str` | `None` | UV layer name (default: active). |
| `attribute_name` | `str` | `None` | Attribute name (default: list attributes only). |
| `group_name` | `str` | `None` | Vertex group name (default: all groups). |
| `include_deltas` | `bool` | `False` | Include per-vertex shape key deltas. |

## Action → Parameter Hints

- `"summary"`: ignores `selected_only`, `uv_layer`, `attribute_name`, `group_name`, `include_deltas`
- `"vertices"` / `"edges"` / `"faces"` / `"normals"`: `selected_only`
- `"uvs"`: `uv_layer` (optional) + `selected_only`
- `"attributes"`: `attribute_name` (optional) + `selected_only`
- `"shape_keys"`: `include_deltas` (optional)
- `"group_weights"`: `group_name` (optional) + `selected_only`

## Examples

```json
{
  "tool": "mesh_inspect",
  "args": {
    "action": "summary",
    "object_name": "Body"
  }
}
```

```json
{
  "tool": "mesh_inspect",
  "args": {
    "action": "vertices",
    "object_name": "Body",
    "selected_only": true
  }
}
```

```json
{
  "tool": "mesh_inspect",
  "args": {
    "action": "shape_keys",
    "object_name": "Face",
    "include_deltas": true
  }
}
```

## Summary JSON (example)

```json
{
  "object_name": "Body",
  "vertex_count": 1234,
  "edge_count": 2456,
  "face_count": 1200,
  "has_uvs": true,
  "has_shape_keys": true,
  "has_custom_normals": false,
  "vertex_groups": ["Spine", "Arm_L", "Arm_R"],
  "modifiers": ["Bevel", "Subdivision"]
}
```

## Replaces

- `mesh_get_vertex_data` → `mesh_inspect(action="vertices", ...)`
- `mesh_get_edge_data` → `mesh_inspect(action="edges", ...)`
- `mesh_get_face_data` → `mesh_inspect(action="faces", ...)`
- `mesh_get_uv_data` → `mesh_inspect(action="uvs", ...)`
- `mesh_get_loop_normals` → `mesh_inspect(action="normals", ...)`
- `mesh_get_attributes` → `mesh_inspect(action="attributes", ...)`
- `mesh_get_shape_keys` → `mesh_inspect(action="shape_keys", ...)`
- `mesh_get_vertex_group_weights` → `mesh_inspect(action="group_weights", ...)`

---

# Rules

1. **Action-based routing**: Each mega tool uses an `action` parameter to route to internal functions.
2. **Internal functions preserved**: Original functions are kept as `_internal_function_name` for backward compatibility.
3. **Parameter validation**: Mega tools validate required parameters and return helpful error messages.
4. **Docstring clarity**: Each action is documented with required/optional parameters.
