# TASK-034: Text & Annotations

**Priority:** 🟡 Medium
**Category:** Modeling Tools
**Estimated Effort:** Low-Medium
**Dependencies:** TASK-004 (Modeling Tools)
**Status:** ✅ **COMPLETED** (2025-12-04)

---

## Overview

Text tools enable **3D typography and annotations** - essential for architectural visualization, signage, logo creation, and dimension labels.

**Use Cases:**
- 3D logos and signage
- Architectural dimension annotations
- Product labels
- Game UI elements (3D text)

---

## Sub-Tasks

### TASK-034-1: text_create

**Status:** ✅ Done

Creates a 3D text object.

```python
@mcp.tool()
def text_create(
    ctx: Context,
    text: str = "Text",
    name: str = "Text",
    location: list[float] | None = None,
    font: str | None = None,  # Path to .ttf/.otf or None for default
    size: float = 1.0,
    extrude: float = 0.0,  # Depth
    bevel_depth: float = 0.0,
    bevel_resolution: int = 0,
    align_x: Literal["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"] = "LEFT",
    align_y: Literal["TOP", "TOP_BASELINE", "CENTER", "BOTTOM_BASELINE", "BOTTOM"] = "BOTTOM_BASELINE"
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a 3D text object.

    Text objects are curves and can be extruded, beveled, and converted to mesh.

    Workflow: AFTER → text_to_mesh (for game export) | modeling_add_modifier
    """
```

**Blender API:**
```python
bpy.ops.object.text_add(location=location or (0, 0, 0))
text_obj = bpy.context.active_object
text_obj.name = name

# Set text content
text_obj.data.body = text

# Font
if font:
    text_obj.data.font = bpy.data.fonts.load(font)

# Geometry
text_obj.data.size = size
text_obj.data.extrude = extrude
text_obj.data.bevel_depth = bevel_depth
text_obj.data.bevel_resolution = bevel_resolution

# Alignment
text_obj.data.align_x = align_x
text_obj.data.align_y = align_y
```

---

### TASK-034-2: text_edit

**Status:** ✅ Done

Modifies existing text object content and properties.

```python
@mcp.tool()
def text_edit(
    ctx: Context,
    object_name: str,
    text: str | None = None,
    size: float | None = None,
    extrude: float | None = None,
    bevel_depth: float | None = None
) -> str:
    """
    [OBJECT MODE] Edits text object properties.

    Only provided parameters are modified, others remain unchanged.
    """
```

**Blender API:**
```python
text_obj = bpy.data.objects[object_name]
if text_obj.type != 'FONT':
    raise ValueError(f"Object '{object_name}' is not a text object")

if text is not None:
    text_obj.data.body = text
if size is not None:
    text_obj.data.size = size
# ... etc
```

---

### TASK-034-3: text_to_mesh

**Status:** ✅ Done

Converts text object to mesh geometry.

```python
@mcp.tool()
def text_to_mesh(
    ctx: Context,
    object_name: str,
    keep_original: bool = False
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts text to mesh.

    Required for:
    - Game engine export (text objects don't export)
    - Mesh editing operations
    - Boolean operations

    Workflow: BEFORE → text_create | AFTER → mesh_* tools, export_*
    """
```

**Blender API:**
```python
text_obj = bpy.data.objects[object_name]
bpy.context.view_layer.objects.active = text_obj
text_obj.select_set(True)

if keep_original:
    bpy.ops.object.duplicate()

bpy.ops.object.convert(target='MESH')
```

**Note:** We already have `modeling_convert_to_mesh` in TASK-008_1 which handles curves/text. Consider if this is redundant or if we need text-specific handling.

---

## Implementation Notes

1. Text objects are type `'FONT'` in Blender
2. Font loading: validate file exists before loading
3. `text_to_mesh` may produce high-poly meshes - consider adding decimate option
4. Consider `modeling_convert_to_mesh` integration - may already handle text

---

## Testing Requirements

- [ ] Unit tests for each tool
- [ ] E2E test: Create text → extrude → convert to mesh → export GLB
- [ ] Test custom font loading
- [ ] Test alignment options
- [ ] Verify modeling_convert_to_mesh handles text (if so, text_to_mesh may be redundant)

---

## Router Integration

For each tool, create metadata JSON file in `server/router/infrastructure/tools_metadata/text/`:

### Example: text_create.json

```json
{
  "tool_name": "text_create",
  "category": "text",
  "mode_required": "OBJECT",
  "selection_required": false,
  "keywords": ["text", "typography", "3d text", "font", "label", "sign", "logo"],
  "sample_prompts": [
    "create 3d text saying Hello",
    "add text label",
    "make a sign with the word EXIT"
  ],
  "parameters": {
    "text": {"type": "string", "default": "Text"},
    "size": {"type": "float", "default": 1.0, "range": [0.01, 100.0]},
    "extrude": {"type": "float", "default": 0.0, "range": [0.0, 10.0]},
    "bevel_depth": {"type": "float", "default": 0.0, "range": [0.0, 1.0]}
  },
  "related_tools": ["text_edit", "text_to_mesh", "modeling_convert_to_mesh"],
  "patterns": [],
  "description": "Creates a 3D text object with optional extrusion and bevel."
}
```

---

## Implementation Checklist (per tool)

Each tool requires implementation in **4 layers** + infrastructure:

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/text.py` | `@abstractmethod def tool_name(...)` |
| Application | `server/application/tool_handlers/text_handler.py` | `def tool_name(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/text.py` | `@mcp.tool() def text_tool_name(...)` |
| Addon | `blender_addon/application/handlers/text.py` | `def tool_name(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `text.tool_name` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` |
| Router Metadata | `server/router/infrastructure/tools_metadata/text/text_tool_name.json` | Tool metadata |
| DI Provider | `server/infrastructure/di.py` | Add `get_text_handler()` if new handler |
| Unit Tests | `tests/unit/tools/text/test_tool_name.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/text/test_tool_name.py` | Full integration tests |

---

## Documentation Updates Required

After implementing these tools, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-034_Text_Annotations.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Move task to Done section |
| `_docs/_CHANGELOG/{NN}-{date}-text-tools.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add tools to MCP tools table |
| `_docs/_ADDON/README.md` | Add RPC commands to handler table |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add tools with arguments |
| `README.md` | Update roadmap checkboxes, add to autoApprove lists |
