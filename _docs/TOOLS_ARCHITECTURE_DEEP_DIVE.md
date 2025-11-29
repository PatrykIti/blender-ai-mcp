# Blender AI MCP – Full Toolset Specification  
Safe / Unsafe / Macro Tools  
For High-Precision AI Modeling (phones, organs, hard-surface, low poly)

---

# A) GROUPED TOOLS (SAFE / PARAMETRIC / RECOMMENDED)

These tools can be a SINGLE tool with multiple operations.

---

## 1) system

Tool: `system`  
Description: Global operations, CRUD on scene, context, reset, modes.

### Possible Operations:
- `set_mode` → OBJECT / EDIT / SCULPT  
- `clear_selection`  
- `focus` (frame selected)  
- `undo`  
- `redo`  
- `save_file` (path)  
- `new_file`  

### Example:
```json
{
  "tool": "system",
  "args": {
    "action": "set_mode",
    "mode": "OBJECT"
  }
}
```

---

## 2) collection

Tool: `collection`  
Description: Full collection management.

### Operations:
- `create`  
- `delete`  
- `move_object`  
- `list_objects`  
- `set_active`  

### Example:
```json
{
  "tool": "collection",
  "args": {
    "action": "create",
    "name": "HouseParts"
  }
}
```

---

## 3) transform

Tool: `transform`  
Description: All transformations in one tool.

### Operations:
- `move`: [x,y,z]  
- `rotate`: axis + degrees  
- `scale`: [x,y,z]  
- `apply`: bool  

### Example:
```json
{
  "tool": "transform",
  "args": {
    "name": "Cube",
    "move": [0, 1, 0],
    "rotate": ["Z", 45],
    "scale": [1, 2, 1],
    "apply": true
  }
}
```

---

## 4) viewport

Tool: `viewport`

### Operations:
- `render_shot` (preview render)
- `frame_object`
- `set_shading`: SOLID / WIREFRAME / MATERIAL

---

## 5) export

Tool: `export`

### Format:
- glb  
- fbx  
- obj  
- usdz  
- stl  
- blend_snapshot  

---

## 6) material

Tool: `material`

### Operations:
- `create` (name, color)  
- `set_param` (roughness, metallic, emission, alpha)  
- `assign` (object, material)  
- `set_texture` (image_path)

---

## 7) uv

Tool: `uv`

### Operations:
- `unwrap_smart`  
- `unwrap_cube`  
- `project_from_view`  
- `pack_islands`

---

## 8) model.create

Tool: `model.create`

### Types:
- cube (size)
- sphere (radius)
- plane (size)
- cylinder (radius, depth)
- cone (radius_top, radius_bottom)

---

# B) SEPARATE (CRITICAL / NOT SAFE TO GROUP)

These tools MUST be separate.  
AI will break topology otherwise.

---

## mesh.extrude
Args:
- distance  
- axis  

---

## mesh.inset
Args:
- thickness  

---

## mesh.bevel
Args:
- amount  
- segments  

---

## mesh.subdivide
Args:
- levels  
- smoothness  

---

## mesh.loop_cut
Args:
- count  
- ratio  

---

## mesh.boolean
Args:
- operation: DIFFERENCE / UNION / INTERSECT  
- target  
- cutter  

---

## mesh.merge_by_distance
Args:
- distance

---

## mesh.triangulate
(no args)

---

## mesh.remesh_voxel
Args:
- voxel_size

---

## mesh.smooth
Args:
- iterations

---

## mesh.delete_selected
(no args)

---

# C) MACRO TOOLS (AI HIGH-LEVEL OPERATIONS)

These are shortcuts that allow AI to create complex models.

---

## model.create_phone_base

Args:
- width  
- height  
- depth  
- corner_radius  
- bezel_width  
- screen_depth  
- chamfer_amount  

---

## mesh.organify

Args:
- relax_strength  
- smooth_passes  
- organic_noise  

Description:  
Creates organic mesh → ideal for heart, lungs, muscles.

---

## mesh.lowpoly_convert

Args:
- target_polycount  
- preserve_silhouette  

---

## mesh.panel_cut

Args:
- depth  
- inset  

Description:  
Cuts panels → phones, laptops, robotics.

---

## model.create_human_blockout

Args:
- proportions_preset  
- scale

---

## mesh.cleanup_all

Args:
- remove_doubles  
- recalc_normals  
- manifold_fix  

---

## model.create_organ_base

Args:
- type: "heart" / "lungs" / "liver"  
- resolution  
- asymmetry  

---

## mesh.sculpt_auto

Args:
- mode: smooth / inflate / grab / draw  
- region  
- intensity  

---

# SUMMARY TABLE

## ✔ SAFE GROUPABLE
system  
collection  
transform  
viewport  
material  
uv  
export  
model.create  

## ❌ CRITICAL SEPARATE
extrude  
inset  
bevel  
subdivide  
loop_cut  
boolean  
triangulate  
remesh  
smooth  
delete_selected  

## ⭐ MACRO HIGH-LEVEL
organify  
lowpoly_convert  
panel_cut  
create_phone_base  
create_organ_base  
human_blockout  
cleanup_all  
sculpt_auto

---

# DOCSTRING STANDARDS & SEMANTIC TAGGING

## 🎯 Purpose
LLMs rely heavily on docstrings to understand tool capabilities, safety, and usage context. 
To minimize token cost while maximizing semantic clarity, we use **concise semantic tags** 
as the first line of every tool docstring.

## 📝 Tag Vocabulary

### Tool Categories (Prefix-Based)

| Prefix | Category | Operating Context | Typical Use |
|--------|----------|-------------------|-------------|
| `scene_*` | Scene Management | Object Mode | High-level scene operations (list, delete, create lights/cameras) |
| `modeling_*` | Object Modeling | Object Mode | Safe, parametric operations (primitives, transforms, modifiers) |
| `mesh_*` | Mesh Editing | Edit Mode | Low-level geometry operations (extrude, bevel, boolean) |
| `macro_*` | High-Level Macros | Any | Complex multi-step workflows (organify, panel_cut) |

### Semantic Tags

**Mode Tags:**
- `[OBJECT MODE]` - Operates in Object Mode (safe context switching)
- `[EDIT MODE]` - Requires Edit Mode (complex state management)
- `[SCENE]` - Global scene-level operation

**Behavior Tags:**
- `[SELECTION-BASED]` - Acts on currently selected geometry/objects
- `[SAFE]` - Query or non-destructive adjustment
- `[NON-DESTRUCTIVE]` - Creates reversible changes (e.g., adds modifier, smooths)
- `[DESTRUCTIVE]` - Permanently modifies or removes data

**Special Semantics:**
- `[UNSELECTED - SELECTED for DIFFERENCE]` - Boolean operation formula (mesh_boolean)

## 📋 Tagging Patterns by Tool Type

### Scene Tools (`scene_*`)

**Safe Operations:**
```python
@mcp.tool()
def scene_list_objects() -> str:
    """
    [SCENE][SAFE] Lists all objects in the scene.
    Returns object names and types in JSON format.
    """
```

**Destructive Operations:**
```python
@mcp.tool()
def scene_delete_object(object_name: str) -> str:
    """
    [SCENE][DESTRUCTIVE] Permanently removes object from scene.
    Cannot be undone via this API.
    
    Args:
        object_name: Name of the object to delete
    """
```

### Modeling Tools (`modeling_*`)

**Safe/Non-Destructive:**
```python
@mcp.tool()
def modeling_add_modifier(object_name: str, modifier_type: str) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Adds modifier to object stack.
    Modifier can be removed or adjusted before applying.
    
    Args:
        object_name: Target mesh object
        modifier_type: ARRAY, MIRROR, BOOLEAN, etc.
    """
```

**Destructive:**
```python
@mcp.tool()
def modeling_apply_modifier(object_name: str, modifier_name: str) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Bakes modifier into mesh geometry.
    Irreversibly alters topology. Cannot be undone.
    
    Args:
        object_name: Target mesh object
        modifier_name: Name of modifier to apply
    """
```

### Mesh Tools (`mesh_*`)

**Selection-Based Non-Destructive:**
```python
@mcp.tool()
def mesh_smooth(object_name: str, iterations: int = 1, factor: float = 0.5) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Smooths selected vertices.
    Uses Laplacian smoothing to refine organic shapes and remove hard edges.
    
    Args:
        object_name: Name of the mesh object to smooth
        iterations: Number of smoothing passes (1-100). More = smoother
        factor: Smoothing strength (0.0-1.0). 0=no effect, 1=maximum smoothing
    """
```

**Selection-Based Destructive:**
```python
@mcp.tool()
def mesh_flatten(object_name: str, axis: Literal["X", "Y", "Z"]) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Flattens selected vertices to plane.
    Aligns vertices perpendicular to chosen axis (X: YZ plane, Y: XZ plane, Z: XY plane).
    
    Args:
        object_name: Name of the mesh object
        axis: Axis to flatten along ("X", "Y", or "Z")
    """
```

**Complex Semantics (Boolean):**
```python
def mesh_boolean(operation: str = 'DIFFERENCE', solver: str = 'EXACT') -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Boolean operation on selected geometry.
    """
```
- Formula: `UNSELECTED (Base) - SELECTED (Cutter)` (for DIFFERENCE)
- `solver='EXACT'`: Uses Exact Boolean solver (robust, default in Blender 5.0+).
- `solver='FLOAT'`: Uses legacy Float solver (fast but error-prone).
- `mesh_boolean` → Points to `modeling_add_modifier(BOOLEAN)` as safer alternative

## 🎨 Design Principles

### 1. Token Economy
- **First line = Tags only** - LLM sees mode/safety immediately
- **Second line = Ultra-concise purpose** - One short sentence
- **Args section = Essential only** - No verbose examples in docstring

### 2. Consistency
- **Reuse exact tag combinations** across tool families
- `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]` appears 10+ times → LLM learns pattern
- Reduces token diversity → Improves model understanding

### 3. Hierarchy
- `scene_*` → High-level, safest, recommended first
- `modeling_*` → Mid-level, parametric, generally safe
- `mesh_*` → Low-level, powerful, requires careful state management

### 4. Cross-References
- `mesh_boolean` → Points to `modeling_add_modifier(BOOLEAN)` as safer alternative
- Guides LLM toward preferred workflows

## 🔍 Tag Decision Tree

```
Is it in Edit Mode?
├─ YES → [EDIT MODE]
│   Does it modify selection?
│   ├─ YES → [SELECTION-BASED]
│   │   Does it delete/alter geometry permanently?
│   │   ├─ YES → [DESTRUCTIVE]
│   │   └─ NO → [NON-DESTRUCTIVE]
│   └─ NO → [SAFE]
│
└─ NO → Is it Object Mode?
    ├─ YES → [OBJECT MODE]
    │   Does it bake/apply/delete?
    │   ├─ YES → [DESTRUCTIVE]
    │   └─ NO → [SAFE] or [NON-DESTRUCTIVE]
    │
    └─ NO → [SCENE]
        Does it remove/reset data?
        ├─ YES → [DESTRUCTIVE]
        └─ NO → [SAFE]
```

## 📚 Reference Tasks
- **TASK-011-5**: Mesh Tool Docstring Standardization
- **TASK-011-6**: Modeling Tool Docstring Standardization  
- **TASK-011-7**: Scene Tool Docstring Standardization

These tasks established the vocabulary and patterns documented here.