# Blender AI MCP – Full Toolset Specification  
Safe / Unsafe / Macro Tools  
For High-Precision AI Modeling (phones, organs, hard-surface, low poly)

---

# A) GROUPED TOOLS (SAFE / PARAMETRIC / RECOMMENDED)

Te narzędzia mogą być JEDNYM toolem z wieloma operacjami.

---

## 1) system

Tool: `system`  
Opis: globalne operacje, CRUD na scenie, context, reset, tryby.

### Możliwe operacje:
- `set_mode` → OBJECT / EDIT / SCULPT  
- `clear_selection`  
- `focus` (frame selected)  
- `undo`  
- `redo`  
- `save_file` (path)  
- `new_file`  

### Przykład:
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
Opis: pełne zarządzanie kolekcjami.

### Operacje:
- `create`  
- `delete`  
- `move_object`  
- `list_objects`  
- `set_active`  

### Przykład:
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
Opis: wszystkie transformacje w jednym toole.

### Operacje:
- `move`: [x,y,z]  
- `rotate`: axis + degrees  
- `scale`: [x,y,z]  
- `apply`: bool  

### Przykład:
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

### Operacje:
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

### Operacje:
- `create` (name, color)  
- `set_param` (roughness, metallic, emission, alpha)  
- `assign` (object, material)  
- `set_texture` (image_path)

---

## 7) uv

Tool: `uv`

### Operacje:
- `unwrap_smart`  
- `unwrap_cube`  
- `project_from_view`  
- `pack_islands`

---

## 8) model.create

Tool: `model.create`

### Typy:
- cube (size)
- sphere (radius)
- plane (size)
- cylinder (radius, depth)
- cone (radius_top, radius_bottom)

---

# B) SEPARATE (CRITICAL / NOT SAFE TO GROUP)

Te narzędzia MUSZĄ być osobno.  
AI inaczej rozwali topologię.

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

To są skróty, które pozwalają AI tworzyć skomplikowane modele.

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

Opis:  
Tworzy siatkę organiczną → idealne do serca, płuc, mięśni.

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

Opis:  
Wycina panele → telefony, laptopy, robotyka.

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

# KONIEC PLIKU MARKDOWN
