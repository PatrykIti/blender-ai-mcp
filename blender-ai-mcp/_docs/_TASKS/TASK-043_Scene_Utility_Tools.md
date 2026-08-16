# TASK-043: Scene Utility Tools

**Priority:** 🔴 High
**Category:** Scene Tools
**Estimated Effort:** Medium
**Dependencies:** TASK-003 (MCP Scene Tools)

---

## Overview

Essential scene utility tools for object management, visibility control, and camera operations. These tools are critical for AI-driven model analysis workflows where precise object inspection and manipulation are required.

**Use Cases:**
- Model analysis workflows (inspecting imported 3D models)
- Object organization (renaming poorly-named objects)
- Selective viewing (isolate specific components)
- Camera navigation (orbit and focus for better inspection)

---

## Sub-Tasks

### TASK-043-1: scene_rename_object

**Status:** ✅ Done

Renames an object in the scene.

```python
@mcp.tool()
def scene_rename_object(
    ctx: Context,
    old_name: str,
    new_name: str
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Renames an object in the scene.

    Workflow: AFTER → scene_list_objects | USE FOR → organizing imported models

    Args:
        old_name: Current name of the object
        new_name: New name for the object

    Returns:
        Success message with old and new name, or error if object not found
    """
```

**Blender API:**
```python
obj = bpy.data.objects.get(old_name)
if obj:
    obj.name = new_name
    return f"Renamed '{old_name}' to '{obj.name}'"  # Note: Blender may add suffix if name exists
else:
    raise ValueError(f"Object '{old_name}' not found")
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def rename_object(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def rename_object(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_rename_object(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def rename_object(...)` with bpy calls |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.rename_object` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_rename_object.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_rename_object.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_rename_object.py` | Full integration tests |

---

### TASK-043-2: scene_hide_object

**Status:** ✅ Done

Hides or shows an object in the viewport and/or render.

```python
@mcp.tool()
def scene_hide_object(
    ctx: Context,
    object_name: str,
    hide: bool = True,
    hide_render: bool = False
) -> str:
    """
    [OBJECT MODE][SCENE][NON-DESTRUCTIVE] Hides or shows an object.

    Workflow: USE FOR → isolating components, cleaning viewport

    Args:
        object_name: Name of the object to hide/show
        hide: True to hide in viewport, False to show
        hide_render: If True, also hide in renders

    Returns:
        Success message with visibility state
    """
```

**Blender API:**
```python
obj = bpy.data.objects.get(object_name)
if obj:
    obj.hide_viewport = hide
    if hide_render:
        obj.hide_render = hide
    state = "hidden" if hide else "visible"
    return f"Object '{object_name}' is now {state}"
else:
    raise ValueError(f"Object '{object_name}' not found")
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def hide_object(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def hide_object(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_hide_object(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def hide_object(...)` with bpy calls |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.hide_object` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_hide_object.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_hide_object.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_hide_object.py` | Full integration tests |

---

### TASK-043-3: scene_show_all_objects

**Status:** ✅ Done

Shows all hidden objects in the scene.

```python
@mcp.tool()
def scene_show_all_objects(
    ctx: Context,
    include_render: bool = False
) -> str:
    """
    [OBJECT MODE][SCENE][NON-DESTRUCTIVE] Shows all hidden objects.

    Workflow: AFTER → scene_hide_object | USE FOR → resetting visibility

    Args:
        include_render: If True, also unhide in renders

    Returns:
        Count of objects made visible
    """
```

**Blender API:**
```python
count = 0
for obj in bpy.data.objects:
    if obj.hide_viewport:
        obj.hide_viewport = False
        count += 1
    if include_render and obj.hide_render:
        obj.hide_render = False
return f"Made {count} objects visible"
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def show_all_objects(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def show_all_objects(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_show_all_objects(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def show_all_objects(...)` with bpy calls |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.show_all_objects` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_show_all_objects.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_show_all_objects.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_show_all_objects.py` | Full integration tests |

---

### TASK-043-4: scene_isolate_object

**Status:** ✅ Done

Isolates an object (hides all others) - similar to Local View.

```python
@mcp.tool()
def scene_isolate_object(
    ctx: Context,
    object_name: str | list[str]
) -> str:
    """
    [OBJECT MODE][SCENE][NON-DESTRUCTIVE] Isolates object(s) by hiding all others.

    Workflow: USE FOR → focused inspection of specific component

    Args:
        object_name: Name or list of names to keep visible (all others hidden)

    Returns:
        Count of objects hidden
    """
```

**Blender API:**
```python
if isinstance(object_name, str):
    keep_visible = {object_name}
else:
    keep_visible = set(object_name)

count = 0
for obj in bpy.data.objects:
    if obj.name not in keep_visible:
        obj.hide_viewport = True
        count += 1
    else:
        obj.hide_viewport = False

return f"Isolated {len(keep_visible)} objects, hid {count} others"
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def isolate_object(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def isolate_object(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_isolate_object(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def isolate_object(...)` with bpy calls |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.isolate_object` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_isolate_object.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_isolate_object.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_isolate_object.py` | Full integration tests |

---

### TASK-043-5: scene_camera_orbit

**Status:** ✅ Done

Orbits the viewport camera around a target point or object.

```python
@mcp.tool()
def scene_camera_orbit(
    ctx: Context,
    angle_horizontal: float = 0.0,  # Degrees
    angle_vertical: float = 0.0,    # Degrees
    target_object: str | None = None,
    target_point: list[float] | None = None
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Orbits viewport camera around target.

    Workflow: USE FOR → inspecting object from different angles

    Args:
        angle_horizontal: Horizontal rotation in degrees (positive = right)
        angle_vertical: Vertical rotation in degrees (positive = up)
        target_object: Object name to orbit around (uses object center)
        target_point: [x, y, z] point to orbit around (if no target_object)

    Returns:
        New camera position and angles
    """
```

**Blender API:**
```python
import math
from mathutils import Matrix, Vector

# Get orbit center
if target_object:
    obj = bpy.data.objects.get(target_object)
    if not obj:
        raise ValueError(f"Object '{target_object}' not found")
    center = obj.location.copy()
elif target_point:
    center = Vector(target_point)
else:
    center = Vector((0, 0, 0))

# Get 3D view and region
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for region in area.regions:
            if region.type == 'WINDOW':
                # Rotate view around center
                rv3d = area.spaces[0].region_3d
                rv3d.view_rotation = rv3d.view_rotation @ Matrix.Rotation(
                    math.radians(angle_horizontal), 4, 'Z'
                ).to_quaternion()
                rv3d.view_rotation = rv3d.view_rotation @ Matrix.Rotation(
                    math.radians(angle_vertical), 4, 'X'
                ).to_quaternion()
                break
        break
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def camera_orbit(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def camera_orbit(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_camera_orbit(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def camera_orbit(...)` with bpy calls |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.camera_orbit` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_camera_orbit.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_camera_orbit.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_camera_orbit.py` | Full integration tests |

---

### TASK-043-6: scene_camera_focus

**Status:** ✅ Done

Centers the viewport camera on an object with optional zoom.

```python
@mcp.tool()
def scene_camera_focus(
    ctx: Context,
    object_name: str,
    zoom_factor: float = 1.0
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Focuses viewport camera on object.

    Workflow: AFTER → scene_set_active_object | USE FOR → centering view on component

    Args:
        object_name: Object to focus on
        zoom_factor: 1.0 = fit to view, <1.0 = zoom out, >1.0 = zoom in

    Returns:
        Success message
    """
```

**Blender API:**
```python
obj = bpy.data.objects.get(object_name)
if not obj:
    raise ValueError(f"Object '{object_name}' not found")

# Select object and focus
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Frame selected in viewport
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        with bpy.context.temp_override(area=area):
            bpy.ops.view3d.view_selected()

        # Adjust zoom
        if zoom_factor != 1.0:
            rv3d = area.spaces[0].region_3d
            rv3d.view_distance /= zoom_factor
        break

return f"Focused on '{object_name}'"
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `@abstractmethod def camera_focus(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | `def camera_focus(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool() def scene_camera_focus(...)` |
| Addon | `blender_addon/application/handlers/scene.py` | `def camera_focus(...)` with bpy calls |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `scene.camera_focus` |
| Router Metadata | `server/router/infrastructure/tools_metadata/scene/scene_camera_focus.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/scene/test_camera_focus.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/scene/test_camera_focus.py` | Full integration tests |

---

## Testing Requirements

- [ ] Unit tests for each tool handler (6 tools × ~3 tests each = ~18 tests)
- [ ] E2E tests for each tool with Blender integration
- [ ] E2E test: Full workflow - list objects → rename → isolate → focus → orbit → inspect

---

## Documentation Updates Required

After implementing these tools, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-043_Scene_Utility_Tools.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Move task to Done section |
| `_docs/_CHANGELOG/{NN}-{date}-scene-utility-tools.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add tools to MCP tools table |
| `_docs/_ADDON/README.md` | Add RPC commands to handler table |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add tools with arguments |
| `_docs/SCENE_TOOLS_ARCHITECTURE.md` | Add detailed tool documentation |
| `README.md` | Update roadmap checkboxes, add to autoApprove lists |

---

## Router Integration

For each tool, create metadata JSON file in `server/router/infrastructure/tools_metadata/scene/`:

### Example: scene_rename_object.json

```json
{
  "tool_name": "scene_rename_object",
  "category": "scene",
  "mode_required": "ANY",
  "selection_required": false,
  "keywords": ["rename", "name", "change name", "relabel"],
  "sample_prompts": [
    "rename the object",
    "change the name of Cube to Box",
    "relabel this object"
  ],
  "parameters": {
    "old_name": {
      "type": "string",
      "description": "Current object name"
    },
    "new_name": {
      "type": "string",
      "description": "New name for the object"
    }
  },
  "related_tools": ["scene_list_objects", "scene_set_active_object"],
  "patterns": [],
  "description": "Renames an object in the scene."
}
```

---

## Implementation Order

Recommended implementation order based on dependencies:

1. **scene_rename_object** (no dependencies, most critical)
2. **scene_hide_object** (foundation for visibility)
3. **scene_show_all_objects** (complements hide)
4. **scene_isolate_object** (uses hide internally)
5. **scene_camera_focus** (independent)
6. **scene_camera_orbit** (independent, more complex)
